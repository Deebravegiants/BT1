### Title
Webhook `shop-domain` (and `topic`/`webhook-id`/`api-version`) headers are not covered by the HMAC signature, allowing cross-tenant spoofing of the shop identity — (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant-identifying `shop` field from an unauthenticated HTTP header (`shop-domain`/`x-shopify-shop-domain`), while `Utils::HmacValidator.validate` only verifies the HMAC over the raw request body (`to_signable_string` returns `@raw_body`). The `shop`, `topic`, `webhook_id`, and `api_version` values are never included in the signed bytes, so they can be modified in transit or forged by anyone who can produce a validly-signed body, without invalidating the signature.

### Finding Description
`ShopifyAPI::Webhooks::Request#shop` reads the tenant identity straight from the `shopify-shop-domain` header: [1](#0-0) 

The HMAC that `Registry.process` checks is computed only over `@raw_body`: [2](#0-1) 

`HmacValidator.validate` signs/verifies exactly that signable string, with the app's single shared `api_secret_key` (the same secret is used for every shop the app serves — it is not shop-scoped): [3](#0-2) 

`Registry.process` accepts the request once the HMAC check on the body passes, then forwards the unauthenticated `request.shop`, `request.topic`, and `request.webhook_id` straight to the app's handler as the trusted tenant identifier: [4](#0-3) [5](#0-4) 

This breaks the identity binding the gem is supposed to guarantee: **shop header value == shop that produced the signed body**. Because the body's HMAC is computed with a secret shared across all shops of the app (not per-shop), and the shop header sits entirely outside the signed bytes, the equality the gem should enforce (`hmac(raw_body, client_secret)` is only valid for the tenant named in `shop-domain`) is never checked. Any request whose body happens to produce a valid HMAC (e.g. a replayed or intercepted real webhook originally sent for the attacker's own shop, or a body an attacker can otherwise cause to be validly signed) can carry an arbitrary `shop-domain` header, and the gem will pass that spoofed shop straight to the merchant's webhook handler as if Shopify itself had asserted it.

### Impact Explanation
This is a cross-tenant identity confusion at the point where the gem hands verified data to the app: the `shop` value the app's `WebhookHandler#handle` uses to decide which merchant's data/session/state to update is not bound to the HMAC signature at all. Apps built on this gem's documented contract (`data.shop`) reasonably trust it as authenticated, per the library's own docs. An attacker who controls or intercepts the webhook channel for one shop (e.g. their own store, which they can freely install the app on) can cause the app to attribute/act on that payload under a different shop's identity, i.e. cross-tenant access/confusion, satisfying the Critical impact bar (cross-tenant access) defined in scope.

### Likelihood Explanation
Requires the attacker to control (or replay) a request whose body validly HMACs under the app's shared secret while presenting a different `shop-domain` header — achievable by any actor who has received (or can trigger) at least one real webhook delivery for a shop they control, since the signing secret is shared across all shops and the shop header is never part of the signed content. This does not require possession of `api_secret_key`, an access token, or any privileged account — only ordinary access to a webhook endpoint the app exposes, matching an unprivileged-internet-user threat model.

### Recommendation
Bind the shop identity to the signature verification, e.g. by including the `shop-domain` (and ideally `topic`/`webhook_id`) header value in the string that is HMAC-verified (mirroring Shopify's actual webhook verification contract, which signs the body but expects the app to independently corroborate the shop via a registered/expected webhook subscription, or by cross-checking the header shop against a shop known to have an active subscription for that `webhook_id`/topic) rather than trusting the raw header unconditionally in `Request#shop`.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker-shop.myshopify.com` and receives a legitimate webhook, capturing `raw_body`, its valid `x-shopify-hmac-sha256`, and other headers.
2. Attacker resends the same `raw_body`/HMAC pair to the app's webhook endpoint but replaces the `x-shopify-shop-domain` header with `victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC successfully (it only checks `raw_body`) at [6](#0-5) , then builds `WebhookMetadata` using the spoofed `request.shop` value [7](#0-6) , causing the app's handler to process/act on the payload as if it belongs to `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
