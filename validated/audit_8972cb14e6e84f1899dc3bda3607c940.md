### Title
Webhook Shop Attribution Not Covered by HMAC Signature Enables Cross-Tenant Webhook Spoofing - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-signable content from the raw request body only, while the `shop` (and `topic`, `webhook_id`, `api_version`) values are read directly from HTTP headers that are never part of the signed payload. `ShopifyAPI::Webhooks::Registry.process` validates the HMAC and, on success, unconditionally trusts the header-derived `shop` value to dispatch tenant-scoped data to the app's webhook handler. This breaks the identity binding: `shop attributed to the webhook payload` ≠ `shop actually covered by the cryptographic signature`.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic tie to the body or the HMAC: [2](#0-1) 

`Registry.process` validates only the HMAC of the body, then immediately builds `WebhookMetadata` using the unauthenticated `request.shop` header value and hands it to the registered handler as the tenant identity: [3](#0-2) 

`HmacValidator.validate` (used both for OAuth callbacks and webhooks) computes the signature purely from `verifiable_query.to_signable_string`, i.e., for webhooks, purely from the body bytes: [4](#0-3) 

Because a single app has one shared `api_secret_key` across every shop that installs it, any request whose body/HMAC pair is valid for shop A is *equally valid* for a forged `shop-domain` header claiming shop B — the header is never part of what's signed. This is exactly the "field acted on but not covered by the HMAC" pattern: the gem verifies *that the body is authentic*, but the caller-visible identity binding (`shop`) that flows into the handler's tenant-scoped logic is never verified.

By contrast, the OAuth callback path correctly includes `shop` inside the signable string, so this is not a systemic design constant across the codebase — it's specific to the webhook path: [5](#0-4) 

### Impact Explanation
An unprivileged actor who can obtain (or trigger) one legitimately-signed webhook body for any shop that installed the app — trivial for merchant-controllable content such as `orders/create` or `products/update` payloads that echo attacker-supplied text — can replay that exact raw body with a forged `shopify-shop-domain` header naming a different, victim shop. `Registry.process` will accept the HMAC as valid and invoke the app's handler believing the payload originated from the victim shop. Any app logic that uses `WebhookMetadata#shop` to select the tenant's stored session, write to the tenant's database records, or make authenticated API calls on the tenant's behalf is exposed to cross-tenant data corruption/disclosure — the gem's own dispatch step performs no verification that ties `shop` to the cryptographically-verified bytes.

### Likelihood Explanation
Exploitability requires only: (1) the ability to submit HTTP POSTs to the app's webhook endpoint (any internet-reachable Shopify app endpoint) and (2) knowledge of one valid `(body, hmac)` pair, which is obtainable by anyone who legitimately triggers a webhook from a shop they control while running the same app (a very low bar, e.g. any developer or freemium install), since `api_secret_key` is shared per app rather than per shop. No credentials, tokens, or privileged access to the target shop are required.

### Recommendation
Bind the `shop` (and `topic`) identity to the signature verification step rather than trusting header values post-hoc. Since Shopify's webhook HMAC is computed over the raw body only (protocol-mandated), the gem should require host applications to cross-check `request.shop` against a shop that is independently known to have a registered/active session for the app before dispatching to the handler, and this expectation should be enforced or at least explicitly surfaced in `Registry.process` (e.g., an optional shop-allowlist check, or documentation making unmistakably clear that `WebhookMetadata#shop` is unauthenticated and must be revalidated by the host app before any tenant-scoped side effect).

### Proof of Concept
1. App is installed on `shop-a.myshopify.com` and `shop-b.myshopify.com` (both use the same `api_secret_key`).
2. Attacker triggers a legitimate webhook from `shop-a` (e.g., updates a product with attacker-chosen JSON-embeddable content), capturing the raw body `B` and the resulting `x-shopify-hmac-sha256` header `H` that Shopify sends to the app.
3. Attacker POSTs to the app's webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` (unchanged, still valid because it signs only `B`), but `x-shopify-shop-domain: shop-b.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)` — passes, since only `B` is checked — at [6](#0-5) 
5. The handler is invoked with `WebhookMetadata` claiming `shop: "shop-b.myshopify.com"`, even though the data actually originated from `shop-a`, at [7](#0-6) 
6. Any handler logic keyed on this `shop` value (loading `shop-b`'s stored session, writing to `shop-b`'s records) now operates on attacker-influenced data mislabeled as belonging to a different tenant.

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
