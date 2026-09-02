### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identity (`shop`) from an HTTP header, but the HMAC that `Registry.process` validates only covers the raw request body, not that header. This lets a party who can obtain any one validly-signed webhook body from the app's own webhook secret (e.g. by installing the app on their own shop and triggering a webhook) replay that body to the app's webhook endpoint with a forged `x-shopify-shop-domain`/`shopify-shop-domain` header pointing at a victim shop. The signature check still passes because it never touches the header, so the handler executes believing the data belongs to the victim tenant.

### Finding Description
`Request#hmac` reads the `hmac-sha256` header, and `Request#to_signable_string` returns only `@raw_body`: [1](#0-0) [2](#0-1) 

`Request#shop`, `#topic`, `#api_version`, and `#webhook_id` are all read straight from headers, which are never part of the signed payload: [3](#0-2) 

`HmacValidator.validate` computes the signature over `verifiable_query.to_signable_string` only: [4](#0-3) 

`Registry.process` validates the HMAC and then unconditionally trusts `request.shop` to construct the tenant-identifying `WebhookMetadata` passed to the app's handler: [5](#0-4) 

This is the identity-binding break described in the source report generalized to this codebase: a field that is *acted on* (the `shop` used to build `WebhookMetadata` and passed to the handler as the tenant key) is not covered by the HMAC that is supposed to authenticate the whole message. The equality that should hold — `shop used to identify tenant == shop cryptographically bound by HMAC` — does not hold; only `body == HMAC(body)` is verified, while `shop` is taken from unauthenticated header bytes.

### Impact Explanation
An unprivileged attacker who has (or creates) their own shop installation of the target app can obtain a legitimately-signed webhook body/HMAC pair for their own shop from Shopify (Shopify signs every webhook it sends with the app's `client_secret`, so any installed merchant will receive validly-signed bodies). They can then replay that exact `(raw_body, hmac)` pair directly to the app's webhook endpoint while substituting the `shop-domain` header for a victim shop domain. `Registry.process` will pass HMAC validation (since it only checks the body) and hand the handler a `WebhookMetadata` claiming the payload is from the victim's tenant. If the host application uses `data.shop` to look up sessions, write tenant-scoped records, or trigger tenant-specific side effects (the documented, expected usage pattern shown in `docs/usage/webhooks.md`), this results in cross-tenant data confusion/injection — one merchant's webhook data being attributed to and processed under another merchant's tenant context. This satisfies the "cross-tenant access" criterion for a High-impact finding.

### Likelihood Explanation
Likelihood is Medium: it requires the attacker to control at least one shop that installs the target app (a low bar — free/dev store installs are trivial to obtain) and the ability to send a raw HTTP POST with attacker-controlled headers to the app's public webhook endpoint (which is, by design, internet-reachable and unauthenticated aside from the HMAC). No access token, `api_secret_key`, or privileged account is required. The main constraint is that the host application must key tenant-sensitive logic off `data.shop` from the webhook handler — which is exactly the pattern the library's own documentation recommends (`data.shop` is documented as "The shop domain of the webhook").

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the value that is authenticated, or independently verify the header-derived `shop` against an out-of-band trusted source (e.g., confirm a session/install record exists for that shop before trusting the webhook) before invoking the handler. At minimum, `Registry.process` (or `Request`) should not treat `request.shop` as authenticated data — the library should document, or better, enforce, that consumers must cross-check the header-provided shop against their own known set of installed shops rather than treating it as verified purely because the surrounding HMAC check passed.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and triggers any subscribed webhook topic (e.g. `orders/create`), causing Shopify to POST a body `B` with a valid `x-shopify-hmac-sha256: HMAC(B, secret)` header and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker captures `(B, HMAC(B, secret))`.
3. Attacker sends a new POST to the app's webhook endpoint with the same body `B` and same `x-shopify-hmac-sha256` header, but sets `x-shopify-shop-domain: victim.myshopify.com`.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `request.to_signable_string` (`= B`) only — it succeeds because the body and HMAC still match.
5. `Registry.process` builds `WebhookMetadata.new(topic: ..., shop: "victim.myshopify.com", body: ..., ...)` and invokes the app's handler, which now processes attacker-controlled data under the victim's tenant identity. [5](#0-4)

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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
