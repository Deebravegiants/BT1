I found a genuine identity-binding issue that matches the bug class in the report, but in a different subsystem: **webhook HMAC verification does not cover the `shop-domain` header**, in `lib/shopify_api/webhooks/request.rb` and `lib/shopify_api/webhooks/registry.rb`.

### Title
Webhook `shop-domain` Header Is Not Covered by HMAC, Allowing Cross-Tenant Spoofing in `Registry.process` - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, excluding the `shop-domain`, `topic`, `webhook-id`, and `api-version` headers from the HMAC-verified data. `Registry.process` validates the HMAC over the body only, then trusts `request.shop` (taken straight from the unauthenticated header) to build the `WebhookMetadata` passed to the app's handler. Any tenant-identifying value acted upon by the handler is therefore not cryptographically bound to the signature that "authenticates" the request.

### Finding Description
The equality this code is implicitly supposed to guarantee is: `shop header value == shop that Shopify actually signed the body for`. That binding is broken because the signable string never includes the shop: [1](#0-0) 

`HmacValidator.validate` only recomputes and compares the signature over `to_signable_string`, i.e. `@raw_body`: [2](#0-1) 

`Registry.process` then uses the *unverified* `request.shop` value to construct the metadata delivered to the registered handler: [3](#0-2) 

Because `hmac-sha256` is computed by Shopify as `HMAC(secret, raw_body)` with no shop binding, any valid `(raw_body, hmac)` pair — including one legitimately generated for the attacker's own shop — remains valid when replayed with an attacker-chosen `shop-domain` header. `HmacValidator.validate` will still return `true`, and `Registry.process` will invoke the app's handler believing the payload originated from the spoofed shop.

### Impact Explanation
This breaks the tenant isolation the HMAC check is meant to provide, matching the "Critical - cross-tenant access" category: an attacker who is a legitimate (but unprivileged, non-victim) merchant/app-installer can receive genuine webhook deliveries for their own shop and replay them with a forged `shop-domain` header to make the host application process data (or perform shop-keyed side effects, e.g. GDPR `customers/redact`, `shop/update`, `app/uninstalled` handling) as if it came from a different, victim tenant — without ever touching the victim's credentials.

### Likelihood Explanation
Likelihood is meaningful but not trivial: the attacker must be able to install the app on a shop they control (ordinary merchant-level access, not privileged) to obtain at least one genuine `(raw_body, hmac)` pair, and must be able to reach the app's public webhook endpoint directly with custom headers (webhook endpoints are plain HTTP(S) routes, so this is feasible for any internet user once they have a valid signed body). The impact depends on how the consuming app's webhook handler uses the `shop` field, but the gem itself provides no mechanism to prevent this cross-tenant spoofing.

### Recommendation
Bind the shop (and ideally topic/webhook-id) into the signable string, or otherwise verify that `request.shop` matches the tenant associated with the signing secret/session before dispatching to handlers — e.g. compute the HMAC over a canonical string that includes the shop header, or require callers to independently validate that the shop in the webhook belongs to an installation this app actually manages, rather than trusting the header outright once `raw_body`'s HMAC checks out.

### Proof of Concept
1. Attacker installs the app on `attacker-shop.myshopify.com` (a normal store signup — no privileged access needed).
2. Shopify sends a legitimate webhook, e.g. `shop/update`, to the app's endpoint:
   - Headers: `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, `X-Shopify-Hmac-Sha256: <valid HMAC of raw_body>`
   - Body: `{"id": ..., "name": "attacker-shop", ...}`
3. Attacker captures this request and resends it to the same app endpoint, changing only the header:
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
   - Body and HMAC left untouched.
4. `ShopifyAPI::Utils::HmacValidator.validate` recomputes `HMAC(secret, raw_body)` — unaffected by the header change — and returns `true`.
5. `Registry.process` builds `WebhookMetadata.new(topic: ..., shop: "victim-shop.myshopify.com", body: <attacker's body>, ...)` and dispatches it to the registered handler, which now processes attacker-controlled data under the victim shop's identity.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-40)
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

        sig { params(signable_string: String, secret: String).returns(String) }
        def compute_signature(signable_string, secret)
          OpenSSL::HMAC.hexdigest(
            OpenSSL::Digest.new("sha256"),
            secret,
            signable_string,
          )
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
