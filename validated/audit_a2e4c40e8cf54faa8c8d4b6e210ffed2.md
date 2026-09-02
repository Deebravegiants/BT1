### Title
Webhook `shop-domain` header is not covered by the HMAC, allowing shop-identity spoofing/cross-tenant webhook injection - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, so the HMAC computed by `Utils::HmacValidator` authenticates the *content* of the webhook but never binds it to the `shop` (tenant) that the request claims to be from. Downstream, `Webhooks::Registry.process` trusts `request.shop` — taken verbatim from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header — as the tenant identity passed to the app's handler. This breaks the identity binding: `shop asserted in header == shop authenticated by HMAC` does not hold, because the HMAC secret (`Context.api_secret_key`) is a single app-level secret shared across every shop that installs the app, not a per-shop secret.

### Finding Description
- `HmacValidator.validate` verifies `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)`. [1](#0-0) 
- For webhooks, `to_signable_string` is defined as just the raw body, and `shop` is read straight from a header with no cryptographic tie to that body: [2](#0-1) 
- `Registry.process` validates only the HMAC over the body, then forwards `request.shop` unchecked to the handler as the authenticated tenant identity: [3](#0-2) 

Because the same `api_secret_key` is used for every shop installed on a given app (it is not per-shop), any merchant who has legitimately installed the app can obtain a genuine `(raw_body, hmac)` pair for content they control (e.g. by triggering a webhook on their own store, or by directly computing an HMAC — no, computing requires the secret; but they can *capture* a real webhook delivery to their own endpoint). Having captured one valid `(body, hmac)` pair, that attacker can replay the exact same body/HMAC to the app's webhook endpoint while substituting `x-shopify-shop-domain` for a victim shop's domain. `HmacValidator.validate` only re-hashes `raw_body`, which is unchanged, so the signature still verifies. `Registry.process` then invokes the app's handler with `WebhookMetadata.shop` set to the victim's domain, even though the payload never actually originated from the victim's Shopify instance.

This is the same bug class as the report's `effectiveCount` bypass: the check that is supposed to gate an action (`effectiveCount` real vouches / "this webhook is authentically from shop X") is evaluated over data that is not actually constrained by the enforcement mechanism (a zero-trust vouch still counts / a shop header not covered by the HMAC still gets treated as authenticated).

### Impact Explanation
Any host application that uses `WebhookMetadata#shop` (as returned by `ShopifyAPI::Webhooks::Registry.process`) to key data, sessions, or business logic per-tenant can have that binding subverted by a request that carries a legitimately-computed HMAC (from the attacker's own installation) but an arbitrary victim `shop` claim. Depending on how the host app uses this value (e.g., updating billing state, deleting data, deactivating a shop on `app/uninstalled`, writing to a shop-keyed session store) this enables cross-tenant data corruption/injection attributed to a shop the attacker does not control — a cross-tenant impact directly reachable through this gem's own webhook-processing API without needing the app's `client_secret` or a leaked token.

### Likelihood Explanation
Requires only that the attacker have (or have had) a legitimate app installation on any shop, and be able to send POST requests directly to the app's public webhook endpoint (bypassing Shopify) — this is squarely in the "unprivileged internet user" threat model, since anyone can install a public Shopify app on a development/trial store. No secrets, tokens, or social engineering are required.

### Recommendation
Bind the `shop` (and ideally `topic`/`webhook_id`) into the value that is HMAC-verified, or otherwise cryptographically/authoritatively confirm that the shop claimed in the header actually corresponds to a shop for which this specific webhook body/HMAC pair was issued (e.g., include the shop domain in the signable string, or cross-check `request.shop` against a per-shop secret/session record before trusting it in `WebhookMetadata`).

### Proof of Concept
1. Install the target app on attacker-controlled shop `attacker.myshopify.com`; trigger any subscribed webhook topic so Shopify delivers `(raw_body, x-shopify-hmac-sha256)` to the app's webhook endpoint.
2. Capture that exact `raw_body` and `x-shopify-hmac-sha256` value.
3. Send a new HTTP POST directly to the app's webhook endpoint with the identical `raw_body` and `x-shopify-hmac-sha256`, but set `x-shopify-shop-domain: victim.myshopify.com`.
4. `HmacValidator.validate` (`lib/shopify_api/utils/hmac_validator.rb:26-31`) recomputes the HMAC over `raw_body` only — it matches, so validation passes.
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-200`) invokes the handler with `shop: request.shop` = `"victim.myshopify.com"`, even though the payload never came from Shopify on behalf of that shop.

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
