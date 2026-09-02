This confirms the asymmetry: for `AuthQuery` (OAuth callback), `shop` **is** included in `to_signable_string` and thus covered by the HMAC. But for `Webhooks::Request`, `to_signable_string` returns only `@raw_body` — `shop`, `topic`, `webhook_id`, and `api_version` come from HTTP headers that are never part of the HMAC computation. [1](#0-0) [2](#0-1) 

### Title
Webhook `shop-domain` (and `topic`/`webhook-id`) headers are not covered by the HMAC, allowing a valid signature for one shop to be replayed under an attacker-chosen shop identity - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC of the raw HTTP body. The `shop`, `topic`, `api_version`, and `webhook_id` values that the handler actually acts on are pulled straight from HTTP headers, none of which are included in the signable string used for HMAC verification.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [3](#0-2) 

`ShopifyAPI::Utils::HmacValidator.validate` computes the HMAC over exactly that signable string and compares it against the `hmac` extracted from the `shopify-hmac-sha256`/`x-shopify-hmac-sha256` header: [4](#0-3) 

`request.shop`, `request.topic`, and `request.webhook_id`, however, are read directly from headers that are entirely outside that HMAC-covered content: [5](#0-4) 

`Registry.process` validates the HMAC of the body, then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` to build the `WebhookMetadata` passed to the app's handler: [6](#0-5) 

This is the exact identity-binding gap described by the report: `hmac_covers(raw_body)` ≠ `fields_acted_on(shop, topic, webhook_id)`. Contrast this with `ShopifyAPI::Auth::Oauth::AuthQuery`, where `shop` **is** folded into `to_signable_string` and therefore is bound by the HMAC: [1](#0-0) 

Because the app's `api_secret_key` is shared across every shop that installs the app (this is not a per-tenant secret), any entity capable of receiving one authentic webhook from Shopify — e.g. by installing the app on their own store — obtains a valid `(raw_body, hmac)` pair. That pair remains valid under `HmacValidator.validate` no matter what `shop-domain`, `topic`, or `webhook-id` header value is attached to the replayed request, because those headers are never hashed.

### Impact Explanation
An attacker who has legitimately received one webhook (via installing the app on their own shop) can replay that exact body+HMAC to the app's public webhook endpoint while substituting `x-shopify-shop-domain` with an arbitrary victim shop's domain (and/or a different `topic`/`webhook-id`). `Registry.process` will pass HMAC validation and hand the handler a `WebhookMetadata` claiming the data belongs to the victim shop. Any host application that uses `data.shop` to select which merchant's records to update (the documented and expected usage pattern, see `docs/usage/webhooks.md`) will apply attacker-supplied payload content against a shop the attacker does not control — i.e., cross-tenant data injection/corruption using forged webhook identity. This satisfies the Critical bucket: cross-tenant access achieved without possessing the target shop's credentials.

### Likelihood Explanation
Requires no `api_secret_key`, no privileged account, and no TLS interception. The only prerequisite is receiving at least one authentic webhook for any shop (trivially satisfied by installing the app on an attacker-owned development/test shop, which most Shopify apps allow), then replaying it with edited headers to the app's own public HTTP endpoint. This is a standard unprivileged-internet-user attack path.

### Recommendation
Bind the identity fields to the HMAC input. At minimum, `Webhooks::Request#to_signable_string` should incorporate `shop`, `topic`, and `webhook_id` (or the library should independently verify, post-HMAC, that the `shop-domain` header matches a shop the caller is authorized to receive webhooks for) so that a valid signature for one shop's payload cannot be replayed under a different shop, topic, or webhook id.

### Proof of Concept
1. Attacker installs the target app on their own shop `attacker-shop.myshopify.com`, receiving a genuine webhook POST with body `B` and header `x-shopify-hmac-sha256: H` (a valid HMAC of `B` under the app's shared `api_secret_key`).
2. Attacker replays the exact same body `B` and header `x-shopify-hmac-sha256: H` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com` (and optionally a different `x-shopify-topic`/`x-shopify-webhook-id`).
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `OpenSSL::HMAC.hexdigest(sha256, api_secret_key, B)` against `H` — this succeeds since `B` and `H` are unchanged: [7](#0-6)  and [3](#0-2) .
4. The registered handler is invoked with `WebhookMetadata.new(topic: request.topic, shop: "victim-shop.myshopify.com", body: ..., ...)`: [8](#0-7) , causing the host app to process attacker-controlled data under the victim shop's identity.

### Citations

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

**File:** lib/shopify_api/webhooks/request.rb (L16-38)
```ruby
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
