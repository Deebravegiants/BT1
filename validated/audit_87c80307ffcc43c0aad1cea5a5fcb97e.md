### Title
Webhook `shop` (and `topic`/`webhook_id`) header trusted for tenant identification while unauthenticated by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating an HMAC over the raw request **body**, then hands the shop domain taken from an **unsigned HTTP header** to the app's handler as the tenant identity for that webhook. Since the HMAC never covers the `shop`, `topic`, or `webhook_id` values, an attacker who can obtain any one genuinely-signed `(body, hmac)` pair from Shopify (e.g. by triggering an event on their own store, which also has the app installed) can replay that body/hmac to the app's public webhook endpoint while substituting an arbitrary victim shop domain in the header, and the signature check still succeeds.

### Finding Description
`ShopifyAPI::Webhooks::Request` exposes `shop`, `topic`, `webhook_id`, and `api_version` purely from HTTP headers: [1](#0-0) 

But the value that gets HMAC-verified is only the raw body: [2](#0-1) 

`HmacValidator.validate`/`validate_signature` compute the digest over `to_signable_string` (the raw body) and compare it to the `hmac` header — nothing else is bound into the signed material: [3](#0-2) 

`Registry.process` performs exactly this body-only check and then immediately trusts `request.shop` (the unauthenticated header) as the tenant for the webhook, forwarding it straight to the app's handler: [4](#0-3) 

The identity binding that should hold is:
`shop_header == shop_that_the_HMAC_actually_authenticates`

but the HMAC only authenticates "this body was produced with the app's `api_secret_key`" — it says nothing about which shop sent it, because the same `api_secret_key` is shared across *every* shop that has the app installed (it's the app's client secret, not a per-shop secret). The `docs/usage/webhooks.md` guidance even states that `Registry.process` "will verify the request did indeed come from Shopify," which is misleading given the shop/topic/webhook_id fields are not covered by that verification: [5](#0-4) 

### Impact Explanation
Because `api_secret_key` is identical for all shops using the app, any merchant who has installed the app on their own (attacker-controlled) shop can legitimately obtain a validly-signed `(raw_body, hmac)` pair for any topic they can trigger in their own store (e.g. `orders/create`, `app/uninstalled`, etc.). By resending that exact body+HMAC to the app's public webhook endpoint with the `x-shopify-shop-domain` (or `shopify-shop-domain`) header rewritten to a victim shop's domain, the HMAC check still passes (it only checks the body), and the app's webhook handler executes attacker-supplied data attributed to the victim tenant. Depending on what the handler does with `data.shop` (e.g. look up the victim's session/access token, mutate victim-scoped records, trigger `app/uninstalled` cleanup for the victim, etc.), this is a cross-tenant data/action injection — Critical impact per the cross-tenant access category.

### Likelihood Explanation
The only prerequisite is that the attacker be a legitimate, unprivileged merchant who has installed the same app (a normal, unprivileged internet-user scenario — no `api_secret_key`, access token, or social engineering required). They only need to capture one webhook delivery to their own store and know the target's shop domain (which is often guessable/known, e.g. `victim-shop.myshopify.com`). This is straightforward to execute.

### Recommendation
Bind the header-derived identity fields into the signed material, or otherwise cryptographically tie the shop to the signature, e.g.:
- Include `shop`, `topic`, and `webhook_id` in `to_signable_string` for webhooks (requires a corresponding change to how the signature is computed/verified, since Shopify currently only signs the body — this may instead need to be enforced at the app layer), or
- Document/require that host applications never treat `data.shop` from `Registry.process` as an authenticated tenant identifier by itself, and instead cross-check it against a known, previously-established session/shop record before performing any tenant-scoped side effects.
- At minimum, update `docs/usage/webhooks.md` to remove the claim that `Registry.process` verifies the request "did indeed come from Shopify" in a way that covers `shop`/`topic`/`webhook_id`, since only the body is authenticated.

### Proof of Concept
1. Attacker installs the vulnerable app on their own shop, `attacker-shop.myshopify.com`.
2. Attacker triggers an event (e.g. creates an order) causing Shopify to POST a genuine webhook to the app's endpoint:
   - Headers: `x-shopify-topic: orders/create`, `x-shopify-hmac-sha256: <valid HMAC of body computed with the app's api_secret_key>`, `x-shopify-shop-domain: attacker-shop.myshopify.com`
   - Body: `{"id": 123, ...attacker-controlled order payload...}`
3. Attacker captures this exact `(body, hmac)` pair.
4. Attacker sends a new POST directly to the app's public webhook endpoint with the same body and same `x-shopify-hmac-sha256` value, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over the (unchanged) raw body and it matches — validation succeeds.
6. `handler.handle(data: WebhookMetadata.new(topic: "orders/create", shop: "victim-shop.myshopify.com", body: <attacker's payload>, ...))` is invoked, and the app's handler processes attacker-controlled data as though it originated from `victim-shop.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

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

**File:** docs/usage/webhooks.md (L123-126)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:

```
