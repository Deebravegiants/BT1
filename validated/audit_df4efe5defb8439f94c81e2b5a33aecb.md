This confirms the finding: the gem's own documented API line 125 of `docs/usage/webhooks.md` states that `Registry.process` "will verify the request did indeed come from Shopify" — implying `data.shop` is trustworthy — yet the `shop` field is never covered by the HMAC. This is not the host application ignoring the API; it's the gem's documented guarantee being broken by its own implementation.

### Title
Webhook `shop` identity is not bound to the HMAC signature, allowing cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` validates a webhook's authenticity solely by HMAC-verifying the raw request body, then trusts the unauthenticated `shop-domain` header as the tenant identity passed to the app's handler. Because the app-level `api_secret_key` used to sign webhooks is shared by every shop that installs the app, any shop that has installed the app can capture one of its own legitimately-signed webhook deliveries and replay the exact same body/HMAC pair while substituting an arbitrary `shop-domain` header, causing the handler to process the payload as if it came from a victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , and `shop` is read straight from the `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header with no cryptographic binding to that body [2](#0-1) . `Registry.process` validates only `Utils::HmacValidator.validate(request)` — which in turn calls `to_signable_string`, i.e. verifies the body bytes only — and then immediately forwards `request.shop` into `WebhookMetadata` for the handler to act on [3](#0-2) . `HmacValidator.validate_signature` computes the signature only from `to_signable_string` [4](#0-3) , so the header carrying the tenant identity is never part of what's authenticated.

The identity binding broken is: *the shop authenticated by the signature* (nothing — the signature authenticates only body bytes and the app's own secret) *≠* *the shop stored/used as the tenant key* (`WebhookMetadata#shop`, taken from an attacker-controllable header). Since the `api_secret_key` used for HMAC signing is the app's single, shared secret across every shop installation, any unprivileged merchant who has installed the app receives real, validly-signed webhook deliveries for their own shop. That merchant can capture the raw body + `hmac-sha256` header from their own webhook and resend it to the app's webhook endpoint with the `shop-domain` header changed to a different (victim) shop's domain. `HmacValidator.validate` still returns `true` (only the body is checked), and `Registry.process` calls the handler with `WebhookMetadata.shop` set to the attacker-chosen victim domain [5](#0-4) .

The gem's own documentation states this exact contract as a guarantee: "call `ShopifyAPI::Webhooks::Registry.process`... This will verify the request did indeed come from Shopify" [6](#0-5) , and separately documents `data.shop` as "The shop domain of the webhook" [7](#0-6) , implying host apps built per this documented API can rely on `data.shop` as an authenticated tenant identifier — which it is not.

### Impact Explanation
This is a cross-tenant identity confusion vulnerability reachable by any unprivileged Shopify merchant who has installed the target app (no `api_secret_key`, access token, or privileged account required — merely normal use of the app as an installed merchant). By replaying a self-generated, validly-signed webhook body under a spoofed `shop-domain` header, an attacker can cause the host application (following the gem's documented usage pattern) to process/store data, trigger side effects, or make Admin API calls using session/state keyed by an arbitrary victim shop domain, rather than their own. Depending on the topic (e.g., `app/uninstalled`, `shop/redact`, `customers/redact`, `app_subscriptions/update`), this can lead to data being attributed to, deleted from, or acted upon on behalf of a shop the attacker does not control — a cross-tenant access impact.

### Likelihood Explanation
Any shop that installs the app already legitimately receives HMAC-signed webhooks signed with the same shared `api_secret_key` used for all other shops, so no secret material needs to be obtained or brute-forced. Only network-level request replay/modification of a header — trivial with any HTTP client — is required, making exploitation straightforward for a merchant-level attacker.

### Recommendation
Bind the shop identity into the authenticated material, or independently authenticate it, before trusting it as the tenant key:
- Include the `shop-domain` header (and ideally `topic`, `api-version`) in `to_signable_string` used for HMAC computation, or
- Cross-check `request.shop` against the shop recorded for the topic/`webhook_id` during registration (per-shop webhook registration is already tracked via the GraphQL Admin client keyed by a specific shop's session), rejecting mismatches, or
- At minimum, update `docs/usage/webhooks.md` to explicitly warn that `data.shop` is unauthenticated and host applications must independently verify shop identity (e.g. against known installed shops) before using it for any tenant-scoped action — though the stronger fix is binding it cryptographically in the gem itself, since it currently claims to "verify the request did indeed come from Shopify."

### Proof of Concept
1. Merchant A installs the app and, through normal use, triggers a webhook (e.g. `products/update`) delivered to the app's webhook endpoint with headers:
   ```
   x-shopify-topic: products/update
   x-shopify-hmac-sha256: <valid-hmac-of-body>
   x-shopify-shop-domain: shop-a.myshopify.com
   ```
   and raw body `B`.
2. Merchant A captures `B` and the `x-shopify-hmac-sha256` value (e.g. via a proxy they control, or their own webhook consumer logs).
3. Merchant A resends the exact same body `B` and `x-shopify-hmac-sha256` value to the app's webhook endpoint, but with `x-shopify-shop-domain: shop-victim.myshopify.com`.
4. `ShopifyAPI::Utils::HmacValidator.validate(request)` computes the HMAC over `@raw_body` only (unchanged) and returns `true` [8](#0-7) .
5. `Registry.process` calls the app's handler with `WebhookMetadata.new(..., shop: "shop-victim.myshopify.com", ...)` [5](#0-4) , and the host app — following the documented example in `docs/usage/webhooks.md` — processes/persists data as if it came from `shop-victim.myshopify.com`, even though Merchant A neither owns nor has an installation on that shop.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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

**File:** docs/usage/webhooks.md (L12-14)
```markdown
`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
```

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
