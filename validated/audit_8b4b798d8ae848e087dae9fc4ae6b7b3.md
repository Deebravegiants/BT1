## Title
Webhook `shop-domain` header is trusted as the tenant identity without being covered by the HMAC signature - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body, then passes the *unauthenticated* `shop-domain` header value straight through to the handler as the tenant identifier. The HMAC binding covers only `raw_body`; it never covers `shop`, `topic`, or any header. This breaks the equality that the report's rule set calls out explicitly: "the shop authenticated versus the shop stored as a session key" / "a field acted on but not covered by the HMAC."

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

and `#shop` is read directly and unauthenticated from the `shopify-shop-domain` / `x-shopify-shop-domain` header: [2](#0-1) 

`Registry.process` verifies the HMAC using `Utils::HmacValidator.validate(request)`, which internally calls `verifiable_query.to_signable_string` (i.e. the raw body) against `Context.api_secret_key`, and then immediately builds the handler payload using `request.shop`, which was never part of the signed bytes: [3](#0-2) [4](#0-3) 

Because `Context.api_secret_key` is a single, app-level secret shared across *every* merchant/tenant that installs the app, any merchant who installs the app can capture a genuine webhook delivered to their own shop (a valid `raw_body` + valid `hmac-sha256` pair, since Shopify signs with the same app secret for all shops). That merchant can then replay the exact same `raw_body`/`hmac` pair to the app's webhook endpoint while substituting an arbitrary value in the `x-shopify-shop-domain` header (e.g. a victim shop's domain). The HMAC check still passes — it only checked the body — but `WebhookMetadata.shop` now reports the attacker-chosen shop.

Binding that is broken, stated as an equality that fails to hold:
`hmac_verified_bytes (raw_body)` ≠ `tenant_identity_used_by_handler (request.shop, from unauthenticated header)`

The library's own documentation instructs consumers to trust exactly this value as the tenant key (`WebhookMetadata#shop`), so any host application following the documented pattern (e.g. looking up the shop's session/access token by `data.shop`, or performing an action "on behalf of" that shop) will act on the wrong tenant.

### Impact Explanation
This is a cross-tenant confusion at the authentication-binding layer inside this gem: the artifact this gem asserts as authenticated ("this webhook is genuinely from shop X because the HMAC is valid") is not actually what the HMAC proves. The HMAC only proves "a party knowing the app's `client_secret`-derived key produced this body" — not which shop it came from. Any of the app's own (or malicious) installed merchants can leverage this to make the host app believe an action or payload belongs to a different, victim shop, satisfying the "cross-tenant access" impact criterion.

### Likelihood Explanation
Requires only an unprivileged attacker who can install the target app on their own shop (a normal, unprivileged step for any public/embedded Shopify app) and can send arbitrary HTTP requests to the app's public webhook endpoint. No `api_secret_key`, access token, or privileged account is required — it is a pure protocol design flaw within `Webhooks::Request`/`Registry.process` in this gem.

### Recommendation
Include the shop domain (and topic/webhook-id if they are also used for security-relevant routing) inside the HMAC-covered signable string, or independently authenticate the `shop-domain` header against a value bound to the API secret/session before trusting it as a tenant key. At minimum, `to_signable_string` should incorporate the `shop-domain` header value so that spoofing it invalidates the signature.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (a normal, unprivileged onboarding step).
2. Shopify delivers a genuine webhook to the app, e.g. `orders/create`, with headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, and some `raw_body`.
3. Attacker resends the exact same `raw_body` and `x-shopify-hmac-sha256` to the app's webhook endpoint, but replaces the header with `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate(request)` recomputes HMAC over `raw_body` only [1](#0-0)  and it matches, so `Registry.process` proceeds [3](#0-2) .
5. `WebhookMetadata.shop` is populated with `victim-shop.myshopify.com` even though the payload/body actually originated from the attacker's shop, and the host application's handler acts on the victim shop's identity.

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
