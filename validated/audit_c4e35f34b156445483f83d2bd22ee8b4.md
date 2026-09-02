I have enough evidence to render a decision on this analog.

### Title
Webhook `shop-domain` header is trusted for tenant routing without being covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, but the `shop` (and `topic`) values used to route the payload to a tenant-specific handler are read from unauthenticated HTTP headers that are never included in the signed content.

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `#shop`/`#topic` are read straight from the `shopify-shop-domain`/`shopify-topic` headers with no cryptographic binding to that value [2](#0-1) . `Registry.process` validates only `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `to_signable_string` (i.e., the body) using the shared `Context.api_secret_key` [3](#0-2) [4](#0-3) . The resulting `WebhookMetadata` — including the unauthenticated `shop` and `topic` — is then handed directly to the app's tenant-scoped handler [3](#0-2) .

Since the app's `client_secret` (used as the HMAC key) is a single per-app secret shared across every installed shop, the HMAC over a given raw body is identical regardless of which shop or topic header accompanies it. Any attacker who can obtain one valid `(raw_body, hmac)` pair — trivially available to them if they operate any shop that has installed the app, since Shopify will deliver a webhook for their own store to the app's public endpoint with a correctly computed HMAC — can replay that exact body/HMAC pair to the same public endpoint while substituting an arbitrary `x-shopify-shop-domain` (and/or `x-shopify-topic`) header value. `HmacValidator.validate` will still pass because it never inspects those headers, and `Registry.process` will dispatch the attacker-supplied body to the handler labeled with a victim shop's domain.

This breaks the intended identity binding: **shop-domain header == shop that authored/owns the signed payload**. The header is verified as "present" but never verified as "the shop that the HMAC secret authenticates for this payload," which matches the "field acted on but not covered by the HMAC" class of bug from the report (the external report's `_wethWithdrawTo` re-entrancy issue is unrelated in mechanism, but the underlying pattern — a check on one thing while acting on a distinct, unguarded thing — is analogous).

### Impact Explanation
If the host application uses `WebhookMetadata#shop` (as `Registry.process` explicitly documents and passes it for this purpose [5](#0-4) ) to decide which merchant record/session to update, an attacker can inject fabricated business-data events attributed to an arbitrary victim shop into a multi-tenant app, causing cross-tenant data corruption or triggering shop-scoped side effects (e.g., fake `orders/create`, `customers/redact`, `app/uninstalled` handling) for a shop the attacker does not control. This is a cross-tenant integrity/isolation break stemming directly from this gem's HMAC verification design.

### Likelihood Explanation
The webhook endpoint is a public internet endpoint (`docs/usage/webhooks.md` shows it wired directly to a public Rails route) and only requires a previously observed valid `(body, hmac)` pair, which is easy for any attacker who is themselves a merchant that has installed the app (they simply capture the webhook Shopify sends them and re-send it with a different shop header). No access to the app's `client_secret`, no privileged account beyond ordinary self-service install, and no TLS interception are required.

### Recommendation
Include the `shop-domain` and `topic` header values inside the string/bytes that are HMAC-verified (or otherwise cryptographically bind them, e.g. by additionally validating the shop domain against a per-shop registered value fetched independently of the request), rather than trusting them purely because a valid body-only HMAC was present. At minimum, document and enforce that consumers must not treat `WebhookMetadata#shop`/`#topic` as attacker-unforgeable for cross-tenant routing decisions without an additional shop existence check against a trusted, out-of-band API call.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers any webhook subscription (e.g. `orders/create`) with an order they fully control, producing raw body `B`.
2. Shopify delivers a POST to the app's public webhook endpoint with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: H` where `H = HMAC-SHA256(client_secret, B)`.
3. Attacker captures `B` and `H` (they own this request/response).
4. Attacker sends their own POST directly to the same public endpoint with body `B`, header `x-shopify-hmac-sha256: H` unchanged, but `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `Webhooks::Request.new` accepts the headers, `HmacValidator.validate` recomputes HMAC over `B` only and it matches `H`, so `Registry.process` calls the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, causing the app to act on data as if it originated from the victim shop.

### Citations

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
