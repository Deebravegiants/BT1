### Title
Webhook `shop` identity is not covered by the HMAC signature, allowing cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the webhook's `shop` (tenant) identity from the `shopify-shop-domain` HTTP header, but the HMAC signature that the gem verifies is computed only over the raw request body. Because the `shop` value that is handed to the app's webhook handler is never bound to the signature, an attacker who can obtain any one genuinely-signed webhook body/HMAC pair (for example by installing the target app on their own store) can replay that exact body+HMAC to the app's webhook endpoint while substituting a different `shopify-shop-domain` header, and the gem will report the webhook as valid and attribute it to the victim shop.

### Finding Description
`Utils::HmacValidator.validate` verifies a signature computed from `verifiable_query.to_signable_string`: [1](#0-0) 

For webhooks, `to_signable_string` returns only `@raw_body` — none of the Shopify headers (topic, shop-domain, webhook-id, api-version) are part of the signed content: [2](#0-1) 

Yet `Request#shop` is read straight from the unauthenticated `shopify-shop-domain` / `x-shopify-shop-domain` header: [3](#0-2) 

`Registry.process` validates only the body HMAC, then forwards `request.shop` (the header value) to the app's handler as the authoritative tenant identifier, with no cross-check that this shop is consistent with the signed payload: [4](#0-3) 

The broken identity binding is:
`shop_bound_by_HMAC (∅, since to_signable_string == @raw_body only)` ≠ `shop_used_downstream (request.shop from the shop-domain header, passed to WebhookMetadata.shop)`

Because the header is not part of the signable content, its value can be swapped freely on a request whose body+HMAC remain valid for the secret, and `Utils::HmacValidator.validate` will still return `true`.

### Impact Explanation
An attacker who obtains one legitimately-signed webhook (e.g., by installing the target app to a shop they control, or capturing/replaying a webhook meant for their own store) can resend that same body and HMAC to the app's public webhook endpoint while changing only the `shopify-shop-domain` header to a victim's shop domain. The gem accepts this as a valid, authentic webhook and passes `shop: <victim-shop>` to the app's `WebhookHandler.handle`, per the documented handler contract: [5](#0-4) 

Since host applications are expected to use `data.shop` to determine which merchant's records/session to act on (as shown in the gem's own documented example, which enqueues work keyed by `data.shop`), this allows an attacker to inject forged, cross-tenant webhook events attributed to a shop they do not control — a cross-tenant data-integrity/authentication issue rooted entirely in this gem's signature-verification scope.

### Likelihood Explanation
Any unprivileged internet user can trigger this: they need only install the target app on any store (including a free/dev store) to receive a genuinely HMAC-signed webhook from Shopify, then replay it against the app's public webhook endpoint with a modified `shop-domain` header. No access token, `client_secret`, or privileged account is required — the `api_secret_key` remains secret; the attacker only reuses a signature Shopify already produced for a body they legitimately received.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) header values into the signable content, or otherwise cross-check the header-derived `shop` against a value cryptographically bound to the payload before trusting it in `WebhookMetadata`. At minimum, `Utils::HmacValidator.validate` (or `Registry.process`) should reject webhooks where the HMAC does not also attest to the `shop-domain` header, e.g. by folding the header into `to_signable_string` for `Webhooks::Request` (mirroring how Shopify's own HMAC verification recommendation binds identity), rather than trusting an unauthenticated header for tenant attribution.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker.myshopify.com` (a store they control) and triggers a webhook event (e.g., `orders/create`). Shopify sends a genuinely HMAC-signed webhook request to the app's endpoint with headers `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, and some `raw_body`.
2. Attacker captures this raw body and HMAC value (they control the receiving endpoint/logs).
3. Attacker crafts a new HTTP request to the app's webhook endpoint using the exact same `raw_body` and `x-shopify-hmac-sha256` value, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` recomputes the HMAC over `@raw_body` only (per `to_signable_string`), which still matches, so `Registry.process` proceeds and calls the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, even though the payload was never actually signed/sent for that shop.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

**File:** lib/shopify_api/webhooks/request.rb (L20-38)
```ruby
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

**File:** docs/usage/webhooks.md (L10-30)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
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
```
