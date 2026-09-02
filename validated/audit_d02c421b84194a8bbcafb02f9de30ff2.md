This confirms the finding. The `docs/usage/webhooks.md` explicitly documents `data.shop` as the authoritative "shop domain of the webhook" that host apps are meant to key their tenant logic on (line 14, 26), while `ShopifyAPI::Webhooks::Request#hmac` verification only covers the raw body, not the shop header.

### Title
Webhook shop-domain header is not covered by HMAC verification, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, then trusts the `shop` value read from an unauthenticated header and hands it to the app's handler as the tenant identity for that webhook.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `shop` is read independently from the `shopify-shop-domain`/`x-shopify-shop-domain` header without being part of that signable string [2](#0-1) . `Registry.process` validates the HMAC via `Utils::HmacValidator.validate(request)` — which hashes only `to_signable_string` (the body) — and then, if it passes, builds `WebhookMetadata` directly from `request.shop`, the unauthenticated header, and hands it to the app-provided handler [3](#0-2) . `HmacValidator.validate` computes the signature purely from `verifiable_query.to_signable_string` and the app secret, with no binding to the shop field [4](#0-3) .

This is the same class of bug as the reported finding: an identity value (the recipient/initiator in the external report, here the `shop` tenant identity) is delivered alongside a verified payload but is itself not covered by the cryptographic check, so the binding `verified(bytes) == authenticated(shop)` does not hold — only the body bytes are authenticated, not which shop they belong to.

Because a merchant that installs the victim app on their own store legitimately receives correctly HMAC-signed webhook bodies for their own shop (using the same app secret shared by all tenants of the app), that same merchant can replay the identical raw body and valid HMAC while swapping the `x-shopify-shop-domain` (or `shopify-shop-domain`) header to name a different shop domain. `Registry.process` will pass HMAC validation (the body/HMAC pair is genuinely valid) and will invoke the handler with `WebhookMetadata.shop` set to the attacker-chosen victim domain [5](#0-4) .

### Impact Explanation
The gem's own documentation instructs host applications to key tenant-scoped work off `data.shop` directly from `WebhookMetadata`, e.g. `perform_later(topic: data.topic, shop_domain: data.shop, ...)` [6](#0-5) . Since this is the gem's documented, intended usage rather than the host app deviating from the API, an app following this documentation will process attacker-controlled body content under a victim shop's identity — enabling cross-tenant data injection/corruption (e.g. an `orders/create` or `app/uninstalled` webhook processed as if it belongs to a different merchant), which fits the "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires only that the attacker be an unprivileged merchant who has legitimately installed the app on their own shop (no access token, secret, or privileged account needed) — they receive real HMAC-signed webhooks for their own store and can freely modify the unauthenticated shop header before replaying the request to the app's public webhook endpoint.

### Recommendation
Include the shop domain (and ideally the webhook id/topic) in the HMAC signable string, or otherwise cryptographically bind the shop header to the payload before `Registry.process` exposes `request.shop` to handlers, mirroring the OAuth `AuthQuery#to_signable_string`, which does include `shop` in its signed parameters [7](#0-6) .

### Proof of Concept
1. Attacker installs the target app on `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`), capturing the raw body `B` and the valid `x-shopify-hmac-sha256` header `H` computed by Shopify with the app's shared secret.
2. Attacker POSTs to the app's webhook endpoint with the same body `B` and header `H`, but sets `x-shopify-shop-domain: victim.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses this into `shop == "victim.myshopify.com"` while `hmac` is computed only from `B` [8](#0-7) .
4. `Utils::HmacValidator.validate` recomputes the HMAC over `B` alone and it matches `H`, so validation succeeds [9](#0-8) .
5. `Registry.process` calls the app's handler with `WebhookMetadata.new(shop: "victim.myshopify.com", body: ..., ...)`, and the app processes attacker-supplied body content under the victim's tenant identity [10](#0-9) .

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L11-23)
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
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end
```

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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

**File:** docs/usage/webhooks.md (L14-29)
```markdown
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```ruby
module WebhookHandler
  extend ShopifyAPI::Webhooks::WebhookHandler

  class << self
    def handle(data:)
      puts "Received webhook! topic: #{data.topic} shop: #{data.shop} body: #{data.body} webhook_id: #{data.webhook_id} api_version: #{data.api_version}"
      perform_later(topic: data.topic, shop_domain: data.shop, webhook: data.body)
    end
  end
end
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
```
