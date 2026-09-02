### Title
Webhook `shop-domain` (and `topic`/`webhook-id`) are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` only verifies the HMAC over the raw request body. All tenant-identifying metadata — `shop`, `topic`, `webhook_id`, `api_version` — is read straight from unauthenticated HTTP headers and passed to the handler as if it had been validated together with the signature.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all pulled from headers with no cryptographic binding to the body/HMAC: [2](#0-1) 

`Registry.process` validates the HMAC (which only covers `raw_body`), and then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` to build the `WebhookMetadata` handed to the app's handler: [3](#0-2) 

`HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` (the body) and compares it against the `hmac` header — it never incorporates `shop`, `topic`, or `webhook_id`: [4](#0-3) 

The identity binding broken is: `HMAC-valid(body) == authenticated(shop, topic, webhook_id)`. In reality `HMAC-valid(body)` only proves the request body was HMAC'd with the app's `client_secret` (shared across *every* shop that installs the app) — it says nothing about which shop or topic the body belongs to. Because a public app's `client_secret` is identical for all merchants who install it, any unprivileged user who installs the app on their own shop can legitimately receive a webhook with a valid HMAC signature, then replay that exact `(raw_body, hmac)` pair to the app's webhook endpoint while substituting the `shopify-shop-domain` (and optionally `shopify-topic`/`shopify-webhook-id`) header to point at a victim shop. `Registry.process` will accept it as authentic (HMAC checks out) and hand the handler a `WebhookMetadata` claiming the payload originated from the victim's shop.

### Impact Explanation
This is a cross-tenant confusion vulnerability: an attacker-controlled `shop` value reaches the app's webhook handler after passing HMAC validation, even though `shop` was never covered by that signature. Any host application that trusts `WebhookMetadata#shop` to select which merchant's session/record to act on (a very common and reasonable pattern given the library asserts the request already "passed" HMAC validation) can be tricked into applying an attacker-crafted payload under a victim shop's identity — i.e., cross-tenant access/write using a webhook payload the attacker fully controls (since they generated it themselves on their own installed shop).

### Likelihood Explanation
Moderate-to-high: it requires no leaked credentials, no `api_secret_key`, and no privileged account — only that the attacker install the (public) app on their own shop to obtain a validly HMAC-signed body, and then forge/replay an HTTP request with a different `shop-domain` header value. This does not depend on the host app misusing the gem's documented API; the gem itself synthesizes and hands out the unauthenticated `shop` field as part of the "validated" `WebhookMetadata` returned after `HmacValidator.validate` succeeds.

### Recommendation
Bind the tenant-identifying headers into the signed material, or otherwise require an out-of-band verified channel for `shop`/`topic`/`webhook_id` (e.g., include them in the signable string per Shopify's newer webhook verification guidance, or require the caller to separately confirm the `shop` header against a known, previously-registered shop/session before trusting it). At minimum, document prominently that `WebhookMetadata#shop`, `#topic`, and `#webhook_id` are NOT covered by the HMAC check in `HmacValidator.validate` and must not be trusted for authorization decisions without additional verification (e.g., cross-checking against the shop for which the webhook was registered).

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` (legitimate, unprivileged action).
2. Attacker triggers an event that causes Shopify to send a webhook to the app; Shopify computes `hmac = HMAC-SHA256(client_secret, raw_body)` and sends headers `shopify-shop-domain: attacker.myshopify.com`, `shopify-hmac-sha256: <hmac>`, `shopify-topic: orders/create`, body `raw_body`.
3. Attacker captures `(raw_body, hmac)`.
4. Attacker sends their own POST directly to the app's webhook endpoint with the same `raw_body`/`hmac` but `shopify-shop-domain: victim.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `raw_body` against `hmac` — validation passes: [5](#0-4) 
6. The app's handler receives `WebhookMetadata` with `shop: "victim.myshopify.com"` and `body` fully controlled by the attacker, despite the request never actually originating from or being authorized by `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
