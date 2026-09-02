## Title
Webhook shop-domain header is not covered by the HMAC signature, enabling cross-tenant webhook forgery - ([File: lib/shopify_api/webhooks/request.rb](lib/shopify_api/webhooks/request.rb))

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, while `shop`, `topic`, `webhook_id`, and `api_version` are all read directly from unauthenticated HTTP headers. `ShopifyAPI::Webhooks::Registry.process` validates the webhook solely with `Utils::HmacValidator.validate(request)`, which computes/compares the HMAC over that body-only signable string, then dispatches the handler with `request.shop` as the tenant identity — a field the HMAC never covers.

### Finding Description
The identity binding that should hold is:
`shop bound into HMAC == shop used to attribute the event to a tenant`

In this gem it does not: [1](#0-0) 

`shop` (and `topic`, `webhook_id`, `api_version`) come from `shopify-shop-domain`/`x-shopify-shop-domain` headers, but `to_signable_string` returns `@raw_body` alone: [2](#0-1) 

`HmacValidator.validate` only ever signs/compares against `to_signable_string`: [3](#0-2) 

`Registry.process` accepts the request once the body-only HMAC checks out, then hands `request.shop` — the unauthenticated header — straight to the handler as the tenant key: [4](#0-3) 

Contrast this with the OAuth callback path, where `shop` *is* part of the signed string (`AuthQuery#to_signable_string` includes `shop`, `host`, `code`, `state`, `timestamp`, all HMAC-covered): [5](#0-4) 

So the same gem shows two different trust models for the same class of Shopify-signed field: OAuth binds `shop` into the signature, but webhook processing does not. Because the app's `client_secret`/`api_secret_key` is only used to protect body integrity, not the header-derived tenant identity, any request that carries a *valid* body+HMAC pair (e.g. one legitimately obtained from a webhook fired for the attacker's own installed shop) can be replayed with an arbitrary `shopify-shop-domain` header pointing at a victim shop. `HmacValidator.validate` still returns true (it never inspects headers), and `Registry.process` invokes the handler with `WebhookMetadata.new(topic: ..., shop: request.shop, ...)` — attributing attacker-controlled content to a tenant the attacker does not control.

### Impact Explanation
This breaks the tenant boundary: a webhook handler is expected to trust that `shop` came from Shopify for that specific shop, since the whole point of HMAC-validating incoming webhooks is to establish "this event genuinely originates from Shopify for shop X." Because `shop` is excluded from the signed payload, an attacker who can obtain any one valid (body, hmac) pair — trivially, by installing the app on their own store and receiving a real webhook — can resubmit that exact body/HMAC with the `shop` header changed to any victim `myshopify.com` domain. Host applications that key session/data lookups off `WebhookMetadata#shop` (the documented, intended usage) will process/store attacker-controlled data under the victim shop's identity, i.e. cross-tenant data injection/misattribution.

### Likelihood Explanation
Exploitation requires no access to the app's `client_secret`, no interception of TLS, and no privileged account: the attacker only needs to install the target app on their own Shopify store (or use any topic that fires webhooks on demand) to legitimately obtain one valid signed body, then replay it against the app's public webhook endpoint with a modified `shop` header. This is directly reachable through the gem's own documented `Registry.process` API, without relying on the host app misusing anything.

### Recommendation
Include `shop` (and ideally `topic`/`api-version`/`webhook-id`) in the signable string used for webhook HMAC validation, or otherwise cryptographically bind the header-derived shop to the signed body before it is passed to handlers as the tenant identity, mirroring the approach already used in `AuthQuery#to_signable_string`.

### Proof of Concept
1. Install the target app on attacker-owned store `attacker.myshopify.com`; trigger a webhook (e.g. `orders/create`) so Shopify sends a legitimately HMAC-signed request with body `B` and header `shopify-hmac-sha256: H` where `H = HMAC(secret, B)`.
2. Capture that request.
3. Resend the same `B` and `H` to the app's webhook endpoint but replace the `shopify-shop-domain` header with `victim.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` recomputes HMAC over `B` only, matches `H`, and returns `true`.
5. `Registry.process` dispatches `handler.handle(data: WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: parsed_body, ...))`, causing the app to act on attacker-supplied content as if it came from `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-43)
```ruby
      sig { override.returns(String) }
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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
