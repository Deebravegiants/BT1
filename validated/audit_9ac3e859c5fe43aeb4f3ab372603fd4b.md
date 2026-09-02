### Title
Webhook shop/topic identity spoofing due to headers not covered by HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then trusts the `shop-domain`, `topic`, `webhook-id`, and `api-version` values taken directly from unauthenticated HTTP headers to build the `WebhookMetadata` passed to the app's handler. Because these header values are never part of the signed content, they can be swapped independently of the signature.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers, none of which feed into the HMAC computation: [2](#0-1) 

`Utils::HmacValidator.validate` re-derives the signature purely from `to_signable_string` (i.e. the raw body) and the app's `api_secret_key`: [3](#0-2) 

`Registry.process` only checks that this body-only HMAC is valid, then unconditionally trusts `request.shop` (and `request.topic`) to build the metadata delivered to the app's handler: [4](#0-3) 

The identity binding that should hold is: `hmac-verified(shop-domain header) == shop value used by the handler`. In this implementation the equality actually enforced is only `hmac-verified(raw_body) == true`, with `shop-domain` (and `topic`) unbound to that signature. An attacker who legitimately owns a Shopify development/test store can subscribe to a webhook topic whose body content is shop-independent (e.g. an `app/uninstalled` webhook, whose body is `{}` in the test fixtures), receive a genuinely-signed delivery from Shopify (signed with the target app's own `client_secret`, since Shopify signs webhooks per-app not per-shop), then resend that exact raw body + HMAC to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` header with a victim shop's domain. `Registry.process` will accept it as valid and hand the handler a `WebhookMetadata` claiming to be from the victim shop.

### Impact Explanation
This breaks the tenant boundary the gem is supposed to enforce for webhook delivery: an unprivileged user (any merchant with their own store using the app) can make the app believe an event happened for a different, unrelated shop. Depending on the handler built on top of this metadata (e.g. deactivating/reinstalling state on `app/uninstalled`, or shop data-erasure on `shop/redact`), this enables cross-tenant interference without possessing the victim's credentials, access token, or the app's `client_secret`.

### Likelihood Explanation
Requires only that the attacker control one legitimate shop installation of the target app (a normal, unprivileged merchant condition) and be able to replay an HTTP request with a modified header to the app's public webhook endpoint — no secret material, TLS interception, or privileged access is needed. The gem itself performs no binding between the authenticated bytes (body) and the trusted identity fields (headers).

### Recommendation
Include the shop domain, topic, and webhook id in the signable content that `HmacValidator` verifies (or otherwise cryptographically bind the header values to the signed payload) so that `Registry.process` cannot be fed a validly-HMAC'd body paired with attacker-controlled `shop`/`topic` headers.

### Proof of Concept
1. Install the app on attacker-owned shop `attacker.myshopify.com`; subscribe to a webhook topic with a shop-independent body (e.g. `app/uninstalled`, body `{}`).
2. Capture the genuine delivery: raw body `{}` and header `X-Shopify-Hmac-Sha256` (valid because HMAC is computed over `{}` with the app's real `client_secret`, as in the request test fixtures).
3. Replay the exact body + HMAC header to the app's webhook endpoint, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate` passes because it only checks the raw body; `Registry.process` invokes the handler with `shop: "victim-shop.myshopify.com"`, causing the app to act as if the event originated from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-28)
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
