The documentation confirms the gem's contract explicitly: `Registry.process` "will verify the request did indeed come from Shopify" (docs/usage/webhooks.md:125) and hands `data.shop` to the app as the trusted tenant identifier (docs/usage/webhooks.md:14, 25-26) — with no caveat that `shop` needs independent verification. That confirms the finding is a defect in this gem's own verification logic, not host misuse of a documented API.

### Title
Webhook shop-domain header is not covered by HMAC verification, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook as authentic once `Utils::HmacValidator.validate(request)` succeeds, and then dispatches `request.shop` to the app's handler as the trusted tenant identifier. However, the HMAC is computed only over the raw body; the `shop-domain` header is never included in the signed material, so it is not bound to the signature at all.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `request.shop` is read straight from the unauthenticated `shopify-shop-domain`/`x-shopify-shop-domain` header with no further validation (not even passed through `ShopValidator`) [2](#0-1) .

`Utils::HmacValidator.validate` recomputes the HMAC using `Context.api_secret_key` (or `old_api_secret_key`) over `verifiable_query.to_signable_string` and only checks that the signature matches — it never touches `shop` [3](#0-2) .

`Registry.process` uses exactly this outcome to gate trust, then builds `WebhookMetadata` directly from `request.shop`, passing it to the app-supplied handler as the shop the event is "for": [4](#0-3) 

Because `api_secret_key` is a single app-wide secret shared across every merchant who installs the app (not a per-shop secret), any shop that installs the app receives genuine Shopify-signed webhook deliveries — `(raw_body, hmac)` pairs — that are valid under that same app-wide secret. Since `shop` is excluded from the signed string, an attacker who controls one (even a free/dev) installation can take one of their own legitimately-received `(raw_body, hmac)` pairs, and replay it against the app's public webhook endpoint while substituting the `shop-domain` header with a victim shop's domain. `HmacValidator.validate` recomputes the same signature (body/secret unchanged) and returns `true`, and `Registry.process` proceeds to invoke the handler with `WebhookMetadata#shop` set to the attacker-chosen victim domain.

This breaks the identity binding: **the shop the app's handler is told to act on() ≠ the shop the signature actually authenticates for()`** — the HMAC authenticates "this app produced/received this body," not "this event belongs to this shop." Any downstream logic that looks up a merchant's session/tenant record keyed by `data.shop` (exactly as shown in the gem's own webhooks documentation) will operate on the wrong tenant's data using the attacker's payload.

### Impact Explanation
This is a cross-tenant confusion vulnerability reachable by any unprivileged internet user who can install the multi-tenant app on their own shop (a normal, unprivileged action for public Shopify apps) and then send a crafted HTTP request to the app's public webhook endpoint. No access token, `client_secret`, or victim credentials are required — only knowledge of one's own valid `(raw_body, hmac)` pair and the victim's shop domain (which is a publicly-known `*.myshopify.com` string). Depending on the topic (e.g. `app/uninstalled`, `customers/redact`, `shop/update`) and how the host app keys its data store off `data.shop`, this can lead to unauthorized state changes, data corruption, or disclosure scoped to a victim tenant — i.e., cross-tenant access.

### Likelihood Explanation
Likelihood is Medium: it requires the attacker to operate their own installation of the target app (trivial for public apps) and to correctly guess/know a target shop's domain, which is often discoverable (storefront URLs, `myshopify.com` subdomains are frequently public). No secret material needs to be stolen; the exploit only relies on the gem's own verification never binding `shop` to the signature.

### Recommendation
Bind `shop` into the HMAC-verified material, or otherwise cryptographically tie the delivered `shop-domain` header to the specific webhook registration/subscription it was issued for (e.g., verify against the shop that the webhook was actually registered for, using data obtained via an authenticated API call, not solely the unauthenticated header). At minimum, `Registry.process` should require the caller to supply the expected shop (from an already-established, authenticated session/tenant context) and reject processing if it doesn't match `request.shop`, rather than propagating the raw header value as the sole tenant identifier.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker-shop.myshopify.com` (normal, unprivileged installation flow).
2. Attacker registers for a webhook topic the app subscribes to (e.g. `customers/create`) and triggers it, causing Shopify to legitimately POST to the app's webhook endpoint with headers:
   - `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - `x-shopify-hmac-sha256: <valid HMAC over body B, computed with the app's shared api_secret_key>`
   - body `B`
3. Attacker captures `(B, valid_hmac)`.
4. Attacker POSTs to the same public webhook endpoint again, keeping body `B` and `valid_hmac` unchanged, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `B` (unchanged) using the same shared `api_secret_key` and finds it matches `valid_hmac` [5](#0-4)  — verification passes despite the shop header being forged.
6. The app's handler is invoked with `WebhookMetadata#shop == "victim-shop.myshopify.com"` and processes the attacker's crafted body as if it originated from the victim shop [6](#0-5) .

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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
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
```
