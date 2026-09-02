## Title
Webhook HMAC only signs the request body, leaving the `shop`, `topic`, `api-version`, and `webhook-id` headers unauthenticated, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body, and `HmacValidator.validate` verifies the HMAC exclusively against that raw body. However, `Registry.process` dispatches the webhook and hands the handler a `WebhookMetadata` struct built from `request.shop`, `request.topic`, `request.webhook_id`, and `request.api_version` — none of which are covered by the HMAC. The identity binding the library implicitly relies on (`hmac == HMAC(body, secret)` implies `shop/topic/webhook_id == authentic`) does not hold, because the signature never binds those header fields.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 

and `hmac`, `shop`, `topic`, `api_version`, `webhook_id` are all pulled independently from headers: [2](#0-1) 

`HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` (the raw body) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` uses this validation as the sole authenticity gate, then trusts `request.shop`, `request.topic`, `request.webhook_id`, `request.api_version` when constructing the metadata passed to the app's handler: [4](#0-3) 

Because the signature never covers `shop-domain`, `topic`, `webhook-id`, or `api-version`, any `(raw_body, hmac)` pair that is valid for one webhook delivery remains valid if those four headers are swapped for arbitrary attacker-chosen values. An unprivileged internet user who can install the app on their own (attacker-controlled) shop — a normal, unprivileged install for a public app — will legitimately receive real webhook deliveries with a valid body+HMAC pair (signed with the app's shared `client_secret`, which is identical across all shops using the app). The attacker can then replay that exact `(body, hmac)` pair to the app's public webhook endpoint while substituting `x-shopify-shop-domain` (and optionally `topic`/`webhook-id`) with a victim shop's domain. `HmacValidator.validate` still succeeds because it only checks the body, and `Registry.process` calls the handler with `WebhookMetadata.new(shop: <attacker-chosen>, ...)`.

### Impact Explanation
This breaks the equality the host application relies on: `HMAC-verified request` ⇒ `shop field is authentic for that shop's data`. Any host app that uses `WebhookMetadata#shop` to key writes/updates into its own per-tenant datastore (a standard and Shopify-recommended pattern) can be made to apply attacker-supplied webhook content under a victim shop's identity — a cross-tenant data-integrity/confusion issue reachable by any unprivileged internet user with no credentials beyond a free/public app install.

### Likelihood Explanation
Requires only: (1) the ability to install the app once as an unprivileged merchant to harvest one valid `(body, hmac)` pair, and (2) the ability to POST to the app's public webhook endpoint with modified headers — both are available to any unprivileged internet user for apps with public installation, with no access to `api_secret_key` or any legitimate credential for the victim shop.

### Recommendation
Include the identifying headers (`shop-domain`, `topic`, `api-version`, `webhook-id`) in the signable string used for HMAC verification (or otherwise cryptographically bind them to the signed payload) in `Request#to_signable_string`, so `HmacValidator.validate` fails if any of those fields are altered independent of the body.

### Proof of Concept
1. Attacker installs the target public app on their own shop `attacker.myshopify.com` and triggers any webhook (e.g., `app/uninstalled`).
2. Attacker's endpoint receives `raw_body`, `x-shopify-hmac-sha256`, `x-shopify-topic`, `x-shopify-shop-domain: attacker.myshopify.com`.
3. Attacker resends the exact same `raw_body` and `x-shopify-hmac-sha256` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate(request)` returns `true` (per `lib/shopify_api/utils/hmac_validator.rb:26-31`, only body is checked), and `ShopifyAPI::Webhooks::Registry.process` invokes the registered handler with `shop: "victim.myshopify.com"` (per `lib/shopify_api/webhooks/registry.rb:198-199`), even though the payload actually originated from the attacker's own shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L11-33)
```ruby
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
        end
```
