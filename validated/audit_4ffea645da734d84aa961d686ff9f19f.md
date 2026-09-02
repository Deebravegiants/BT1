This confirms the vulnerability. The `x-shopify-shop-domain`/`shopify-shop-domain` header, `topic`, and `webhook-id` headers are entirely outside the HMAC coverage — `to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop`, `topic`, and `webhook_id` are all read from unauthenticated headers [2](#0-1) . `Registry.process` validates only the HMAC of the body, then trusts `request.shop` and `request.topic` from those headers to build `WebhookMetadata` passed to the app's handler [3](#0-2) .

### Title
Webhook tenant/topic identity spoofing via unauthenticated headers not covered by HMAC - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` derives `shop`, `topic`, and `webhook_id` from raw HTTP headers, while `Utils::HmacValidator` (via `to_signable_string`) authenticates only the raw request body. `Registry.process` uses the validated-body request but trusts the unauthenticated `shop` header when constructing `WebhookMetadata` for the host application's handler.

### Finding Description
`Request#to_signable_string` returns `@raw_body` only [1](#0-0) . `HmacValidator.validate` computes the HMAC over exactly that signable string and compares it against the `hmac` value read from the `hmac-sha256` header [4](#0-3) . The `shop`, `topic`, and `webhook_id` values are read directly from HTTP headers and are never included in the signed content [2](#0-1) .

`Registry.process` checks only `Utils::HmacValidator.validate(request)` (i.e., body authenticity), then immediately uses `request.shop` and `request.topic`, taken from the unauthenticated headers, to look up a handler and build the `WebhookMetadata` delivered to the app: `handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop, body: request.parsed_body, ...))` [3](#0-2) .

This breaks the intended binding: `shop asserted to handler == shop that produced the signed bytes`. Since the header carrying the shop identity is outside the HMAC's coverage, an attacker who obtains one validly-signed `(raw_body, hmac)` pair (e.g., from their own store's webhook delivery, which they legitimately receive) can resend that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` header value. The HMAC still validates (it only ever checked the body), but `Registry.process` reports the attacker-chosen shop identity to the host application's handler, along with the topic of the attacker's choosing (also unauthenticated).

### Impact Explanation
This allows cross-tenant identity confusion at the webhook boundary: the gem certifies a payload as "authentically from Shopify" via HMAC, but hands the host application a forged tenant identity (`shop`) and topic. Any host application logic that trusts `WebhookMetadata#shop` for tenant-scoped actions (e.g. selecting which merchant's data to update/delete, GDPR `customers/redact`/`shop/redact` processing, deciding which store's stored access token/session to act on) can be made to act on behalf of, or attribute attacker-supplied data to, a different tenant than actually sent it — a cross-tenant access/confusion condition.

### Likelihood Explanation
Exploitation requires the attacker to control (or have legitimately received) at least one validly-signed webhook body/HMAC pair from Shopify for their own shop — something achievable by any developer/merchant who installs the app on their own store, since webhook HMACs use the app's shared secret across all installs. No access token, `client_secret`, or privileged access is required; only header manipulation against the app's public webhook endpoint.

### Recommendation
Include the shop domain (and ideally the topic and webhook id) in the HMAC-signed content, or otherwise cryptographically bind the header-derived identity fields to the signed payload before they are trusted. Short term: have `Registry.process` cross-check `request.shop` against the shop embedded in the parsed body / a value obtained via a trusted side channel (e.g., look up the webhook subscription by the signed webhook id via the Admin API for the shop it claims to be) rather than trusting the raw header value directly.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and receives a legitimate webhook delivery: raw body `B`, with header `x-shopify-hmac-sha256: H` (valid HMAC of `B` under the app's secret) and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker replays the same `raw_body: B` and `x-shopify-hmac-sha256: H` to the app's webhook endpoint, but sets `x-shopify-shop-domain: victim.myshopify.com` (and optionally a different `x-shopify-topic`).
3. `HmacValidator.validate(request)` in `lib/shopify_api/utils/hmac_validator.rb` succeeds because it only checks `B` against `H`.
4. `Registry.process` in `lib/shopify_api/webhooks/registry.rb` invokes the registered handler with `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: JSON.parse(B), ...)`, causing the host application to process attacker-controlled data under the victim shop's identity.

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
