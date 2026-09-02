### Title
Webhook shop attribution is not bound to the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from an HTTP header that is **not** covered by the HMAC signature it verifies. The HMAC only authenticates the raw request body; the `shop-domain` header used by webhook consumers to attribute the payload to a specific merchant/session is trusted independently. Because a single app-wide `client_secret` is used to compute the HMAC for every shop that has the app installed, any merchant who can obtain one valid `(body, hmac)` pair for their own shop can replay it against the same endpoint while substituting a different `shop-domain` header value, producing a request that passes signature verification but is misattributed to a victim shop.

### Finding Description
`Request#hmac` reads the signature from the `shopify-hmac-sha256`/`x-shopify-hmac-sha256` header, and `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) [2](#0-1) 

The tenant-identifying `shop` value is read from a separate, unsigned header: [3](#0-2) 

`Utils::HmacValidator.validate` only checks that the received HMAC matches `HMAC(secret, to_signable_string)`, i.e. it verifies the body bytes, never the `shop` header: [4](#0-3) 

This is exactly the binding break called out in the rules: **shop authenticated (via HMAC over body) ≠ shop stored/used as the tenant/session key (`Request#shop`)**. Since the same `Context.api_secret_key` is shared across all shops that install the app, `HMAC(secret, body)` is identical regardless of which shop the body nominally belongs to. Any two requests with the same raw body and a valid signature will pass `HmacValidator.validate` no matter what `shop-domain` header accompanies them.

### Impact Explanation
Any party who can obtain one legitimately-signed `(body, hmac)` pair — trivially available to any merchant who installs the app on their own store and receives a real webhook delivery from Shopify — can resend that exact body/HMAC pair to the app's webhook endpoint while spoofing the `X-Shopify-Shop-Domain` (or `Shopify-Shop-Domain`) header to name a different, victim shop. Because verification never binds the header to the signature, `Request#shop` will report the attacker-chosen victim shop while the HMAC check still succeeds. Host applications built on this gem dispatch webhook payloads keyed by `request.shop` (see `lib/shopify_api/webhooks/registry.rb`) to load/act on that shop's session and to persist or react to the payload contents. This lets an unprivileged merchant inject attacker-controlled webhook data attributed to another merchant's tenant — a cross-tenant boundary violation.

### Likelihood Explanation
Exploitation requires no secret material, no privileged account, and no host-application misuse of documented API — only (a) the attacker's own legitimate app installation to harvest one valid signed payload, and (b) the ability to send an HTTP request with custom headers to the app's public webhook endpoint. Both are available to any ordinary merchant using the app, making this a realistic, low-effort cross-tenant attack path rather than a theoretical one.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook-id`) header value into the signed material verified by `HmacValidator`, or have `Utils::HmacValidator`/`Request` reject requests whose header-derived `shop` cannot be independently correlated with the topic/resource referenced in the body. At minimum, document and enforce that consumers must cross-check `request.shop` against the shop associated with the resource IDs contained in the (HMAC-verified) body before trusting it as a session key.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker-shop.myshopify.com`.
2. Shopify sends a real webhook (e.g. `orders/create`) to the app's webhook endpoint with headers `X-Shopify-Hmac-Sha256: <H>` and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`, and body `B`; `H = HMAC-SHA256(api_secret_key, B)`.
3. Attacker captures `(B, H)` (e.g., by pointing the webhook to a URL they log, or replaying the raw HTTP request they receive).
4. Attacker sends a new POST to the same endpoint with body `B`, header `X-Shopify-Hmac-Sha256: H` unchanged, but `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. `Webhooks::Request.new` accepts the request (all required headers present) and `Utils::HmacValidator.validate` succeeds because it only checks `HMAC(api_secret_key, B) == H`, which is unaffected by the shop header change.
6. The host application's registry dispatches the handler with `shop = "victim-shop.myshopify.com"` and the attacker-controlled body `B`, causing the app to process/store attacker data under the victim's tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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
