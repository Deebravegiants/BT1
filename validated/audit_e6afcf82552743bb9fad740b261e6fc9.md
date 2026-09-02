### Title
Webhook `shop-domain` header is not bound to the HMAC signature, enabling cross-tenant webhook forgery - (`lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/utils/hmac_validator.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
Shopify webhook processing in this gem authenticates only the request body against the app's shared `client_secret`, but it never binds the `shop-domain` header (or `topic`, `webhook_id`, `api_version`) to that signature. Any actor who has legitimately received one valid webhook for their own shop (i.e. any merchant who has installed the app) can reuse the same body+HMAC pair while substituting an arbitrary `shop-domain` header, and `Registry.process` will accept it and hand the forged shop identity straight to the app's handler.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`ShopifyAPI::Utils::HmacValidator.validate_signature` computes/compares the HMAC exclusively over `verifiable_query.to_signable_string`: [2](#0-1) 

Meanwhile, `request.shop` (parsed from the unauthenticated `x-shopify-shop-domain`/`shopify-shop-domain` header) is exposed as an accessor and is completely independent of the signature: [3](#0-2) 

`Registry.process` verifies only the HMAC of the body, then immediately trusts `request.shop` as the tenant identity when constructing `WebhookMetadata` for the app-supplied handler: [4](#0-3) 

This breaks the intended binding:
`hmac_valid(body, client_secret) == true` should imply `shop-domain == the shop that actually generated this body`.
In reality the equality that holds is only `hmac_valid(body, client_secret) == true`; `shop-domain` is an unauthenticated, attacker-controllable header value that travels alongside the body but is never covered by the signature.

Critically, the signing secret (`Context.api_secret_key`, i.e. the app's `client_secret`) is **shared across every shop that has installed the app** — it is not per-tenant. So a party who controls Shop A (a legitimate install) receives real webhook deliveries with a valid HMAC computed over a body they can fully observe. They can then replay that exact `raw_body` + `hmac-sha256` value to the app's public webhook endpoint while setting `x-shopify-shop-domain: shop-b.myshopify.com`. `HmacValidator.validate` will return `true` (the body/secret pair is genuinely valid), and `Registry.process` will dispatch to the handler with `WebhookMetadata#shop == "shop-b.myshopify.com"`, even though shop B never sent this webhook.

### Impact Explanation
This is a cross-tenant identity-confusion vulnerability: it lets an attacker who is a customer of the app (installed on their own shop) inject data that is falsely attributed to another merchant's shop into the host application's webhook processing pipeline (e.g. fake `orders/create`, `app/uninstalled`, `customers/data_request`, or GDPR-relevant webhooks attributed to a victim shop). Depending on what the host app does with `WebhookMetadata#shop` (commonly used as a lookup/foreign key to load or mutate that shop's stored session/data), this can lead to cross-tenant data corruption, spoofed uninstall/compliance events, or forged business events for a shop the attacker does not control. This matches the "cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is not trivial to reach because: (1) the attacker must operate their own legitimate installation of the target app to obtain a genuinely-signed body+HMAC pair, and (2) they must know or guess the victim shop's exact domain, and (3) the forged payload's *contents* still reflect the attacker's own shop's data (only the `shop` header is spoofable, not the JSON body's authenticity relative to a specific shop) — but many webhook bodies (e.g. `app/uninstalled`, `shop/redact`) carry generic/predictable shapes that don't need shop-specific data to be damaging. Any multi-tenant app built on this gem that trusts `WebhookMetadata#shop` for tenant routing without independent verification (e.g. checking the shop against a known installed-shops list before trusting it) is exposed.

### Recommendation
Bind the shop identity to the authenticated signal instead of trusting an unauthenticated header in isolation:
- Cross-check `request.shop` against the caller's own store of installed/known shops before processing (fail closed if the shop hasn't installed the app or the topic wasn't registered for it).
- Where possible, also validate that the webhook's registered delivery target/shop matches via the Admin API (e.g., re-confirming shop install state), rather than trusting the header value alone.
- Document explicitly in `docs/usage/webhooks.md` that `shop` on `WebhookMetadata` is not itself HMAC-authenticated and must be cross-checked by the consuming application before being used as a tenant key.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and receives a legitimate webhook delivery, e.g. topic `app/uninstalled`, with body `raw_body` and header `x-shopify-hmac-sha256: H`, where `H = Base64(HMAC-SHA256(client_secret, raw_body))`.
2. Attacker sends a forged HTTP POST directly to the app's public webhook endpoint with:
   - Body: the exact same `raw_body`
   - Header `x-shopify-hmac-sha256: H` (unchanged, still valid because the key `client_secret` is shared across all shops)
   - Header `x-shopify-shop-domain: victim-shop.myshopify.com` (forged)
   - Header `x-shopify-topic: app/uninstalled`
3. The host app calls `ShopifyAPI::Webhooks::Registry.process(ShopifyAPI::Webhooks::Request.new(raw_body:, headers:))`.
4. `Utils::HmacValidator.validate` returns `true` because it only recomputes the HMAC over `raw_body` [5](#0-4) .
5. `Registry.process` dispatches to the registered handler with `WebhookMetadata.new(..., shop: "victim-shop.myshopify.com", ...)` [6](#0-5) , causing the host application to treat this attacker-triggered event as originating from the victim shop.

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
