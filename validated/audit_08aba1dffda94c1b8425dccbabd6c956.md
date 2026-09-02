## Analysis

The bug-class in the report (`setbidtobuy` acting on a field without checking a controlling flag) maps to a genuine identity-binding gap in `ShopifyAPI::Webhooks::Request`/`ShopifyAPI::Webhooks::Registry.process`: the `shop` field used to route webhook data to a tenant is never covered by the HMAC signature the gem verifies.

`ShopifyAPI::Webhooks::Request` derives `shop` purely from the `x-shopify-shop-domain`/`shopify-shop-domain` HTTP header: [1](#0-0) 

but the value that is actually HMAC-verified (`to_signable_string`) is only the raw request body: [2](#0-1) 

`Utils::HmacValidator.validate` computes the signature strictly from `to_signable_string` (the raw body) and the app's `api_secret_key`, and never touches `shop`, `topic`, or any other header: [3](#0-2) 

`Webhooks::Registry.process` then trusts `request.shop` — the unauthenticated header — to build the tenant-identifying metadata passed to the app's handler: [4](#0-3) 

### Title
Webhook `shop` (tenant) identity is not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook solely by recomputing an HMAC over the raw body (`Request#to_signable_string`) and comparing it against the `X-Shopify-Hmac-Sha256` header, using the app's shared `client_secret`. The `shop` (tenant identity) used downstream by the app's handler comes from the separate, unauthenticated `X-Shopify-Shop-Domain` header, which is not part of the signed payload. The equality the code implicitly assumes — "HMAC-authenticated body" == "body legitimately originated for the `shop` header value" — does not hold, because the app's webhook secret is shared across all shops that install the app, and the signature is computed only over the body.

### Finding Description
Any attacker who can install the app on a shop they control (e.g. a free Shopify development store) can register a webhook, receive a legitimately Shopify-signed request `(raw_body, X-Shopify-Hmac-Sha256)` at their own endpoint, and then replay that exact `(raw_body, hmac)` pair directly against the target app's shared webhook endpoint while substituting an arbitrary victim `X-Shopify-Shop-Domain` header value. Because:
- `HmacValidator.validate` only checks `raw_body` against the app's secret (`lib/shopify_api/utils/hmac_validator.rb:12-31`), and
- `Request#shop` is read straight from the spoofable header (`lib/shopify_api/webhooks/request.rb:20-23`), and
- `Registry.process` passes that unauthenticated `shop` value straight into `WebhookMetadata` for the app's handler (`lib/shopify_api/webhooks/registry.rb:198-199`),

the signature check passes even though the `shop` claim was never authenticated. The handler then processes attacker-controlled body data under a victim tenant's identity.

### Impact Explanation
This breaks the tenant isolation guarantee the HMAC check is meant to provide: `hmac_valid(body) == body_belongs_to(shop)` does not hold because `shop` is outside the signed scope. Any consuming app that uses `WebhookMetadata#shop` to select which tenant's records to create/update/delete (a standard pattern) can be made to apply attacker-supplied webhook payloads to another merchant's data — i.e., cross-tenant access/write, satisfying the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Requires only an unprivileged Shopify developer account (free dev store) capable of installing the target app and triggering any webhook topic the app registers for; no access to the app's `client_secret`, TLS interception, or privileged accounts is needed. The forged request is a straightforward direct HTTP POST to the app's public webhook endpoint.

### Recommendation
Include the tenant-identifying header(s) (at minimum `shop`, ideally `topic`/`webhook_id`) inside the HMAC-covered signable string, or independently verify that the `shop` header corresponds to a shop with a valid, stored session/installation for this app before dispatching to the handler, rather than trusting the header value outright.

### Proof of Concept
1. Install the target app on an attacker-owned dev store; register a webhook for any topic.
2. Capture the resulting request Shopify sends: raw body `B` and header `X-Shopify-Hmac-Sha256: H` (valid because `H = HMAC-SHA256(client_secret, B)`, verified by `HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb:12-31`).
3. Send a new POST directly to the app's public webhook endpoint with the same body `B` and header `H`, but set `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Webhooks::Request#shop` returns `"victim-shop.myshopify.com"` (`lib/shopify_api/webhooks/request.rb:20-23`); `HmacValidator.validate` still succeeds because it never inspects the shop header (`lib/shopify_api/utils/hmac_validator.rb:12-31`); `Registry.process` invokes the handler with `shop: "victim-shop.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:198-199`), causing the app to act on attacker data under the victim's tenant identity.

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
