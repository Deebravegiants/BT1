### Title
Webhook `shop-domain` Header Not Bound to HMAC Signature Enables Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, while the `shop` identifier used to route/attribute the event is read from an unauthenticated header that is never part of the signed material. Any bytes captured with a valid `(body, hmac)` pair can be replayed with an attacker-chosen `shop-domain` header and will still pass verification, breaking the binding `hmac_covers(bytes) == bytes_trusted_as_tenant_identity(bytes)`.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

while `#shop` is pulled straight from the `shop-domain` (or `x-shopify-shop-domain`) header, independent of that signed body: [2](#0-1) 

`Utils::HmacValidator.validate` computes the HMAC only over `verifiable_query.to_signable_string` (i.e. the body) and compares it to the supplied `hmac`: [3](#0-2) 

`Registry.process` uses exactly this check as the sole authentication gate before handing the request, including the unverified `request.shop`, to the app's handler: [4](#0-3) 

The equality the gem is implicitly (and incorrectly) asserting is:
`hmac_valid(body, hmac) ⇒ shop_header_is_authentic`

But the real invariant only guarantees `hmac_valid(body, hmac) ⇒ body_is_authentic_for_some_shop`. The `shop` value is never covered by the HMAC, so it is fully attacker-controlled while the request still passes as "verified."

This mirrors the reported bug class exactly: a value used to identify/act on a resource (here, the tenant/shop) is not covered by the same integrity check (`clean_and_check_token_records`/`resolve` mismatch in the report ⇔ HMAC-body vs. header-shop mismatch here) that is relied upon to authorize the operation.

### Impact Explanation
An unprivileged internet user who can install the target app on their own shop (a normal, unprivileged onboarding action) will legitimately receive real webhooks from Shopify, each with a valid `(body, hmac)` pair signed with the app's real `client_secret`. Many webhook topics have small, fixed, or attacker-controllable bodies (e.g. `{}` for several compliance/lifecycle topics). The attacker can:
1. Capture a legitimate `(body, hmac)` pair delivered for their own shop.
2. Replay that exact body and HMAC to the app's webhook endpoint while substituting the `shop-domain` header with a victim shop's domain.
3. `HmacValidator.validate` still returns `true` because it only checks body integrity, and `Registry.process` forwards `data.shop = <victim shop>` to the app's handler as if Shopify itself had asserted this pairing.

Depending on what the host app's handler does with `data.shop` (e.g., marking a shop as uninstalled, redacting/deleting shop data, disabling billing, flipping feature flags, writing shop-scoped records), this is a cross-tenant boundary violation attributable entirely to the gem's failure to bind the tenant identifier to the signed payload. This satisfies the Critical "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is realistic but requires the attacker to have their own legitimate install of the target app (a normal, unprivileged action any internet user can take by installing a public app on a store, including free dev stores) and to identify a webhook topic where the raw body is fixed/known/reusable across shops. No secrets, tokens, or privileged access are required — only observation of headers vs. body in a delivery the attacker legitimately receives for their own tenant.

### Recommendation
Bind the shop identity to the signed material before trusting it:
- Include the shop-domain header (and ideally topic/webhook-id) in the signable string validated by `HmacValidator`, or
- Cross-check `request.shop` against an independently derived, trusted mapping (e.g., look up the session/shop by a value that is itself covered by the HMAC, or validate against Shopify's API using the topic/webhook id) before acting on `WebhookMetadata#shop`.
- At minimum, document loudly that `Webhooks::Request#shop` is unauthenticated and must not be trusted for tenant-scoped side effects without additional verification.

### Proof of Concept
1. Install the target app on shop `attacker.myshopify.com`.
2. Wait for (or trigger) a webhook delivery for a topic whose body is `{}` (many compliance/lifecycle topics qualify). Capture the raw body and the `X-Shopify-Hmac-Sha256` header value — this HMAC is valid for `{}` under the app's real secret.
3. Send a forged HTTP request to the app's webhook endpoint with:
   - Body: `{}` (unchanged)
   - `X-Shopify-Hmac-Sha256`: the captured, still-valid HMAC
   - `X-Shopify-Shop-Domain`: `victim.myshopify.com` (attacker-chosen)
   - `X-Shopify-Topic`: same topic
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the body against the HMAC (`lib/shopify_api/utils/hmac_validator.rb:12-31`, `lib/shopify_api/webhooks/request.rb:35-38`).
5. The handler is invoked with `WebhookMetadata` whose `shop` field is `"victim.myshopify.com"` (`lib/shopify_api/webhooks/registry.rb:198-199`, `lib/shopify_api/webhooks/request.rb:20-23`), even though Shopify never sent this event for that shop.

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
