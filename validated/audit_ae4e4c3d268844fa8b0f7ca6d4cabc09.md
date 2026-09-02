I have enough evidence now to state the finding clearly.

### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes and validates its HMAC over the raw body only, while the `shop` (and `topic`/`webhook_id`/`api_version`) values used by `ShopifyAPI::Webhooks::Registry.process` to attribute the event to a tenant come from unauthenticated HTTP headers that are excluded from the signed data.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Request#shop` is read directly from the `shopify-shop-domain`/`x-shopify-shop-domain` header with no cryptographic binding to the signature: [2](#0-1) 

`Registry.process` only checks `Utils::HmacValidator.validate(request)` (which validates the body against the app-wide `Context.api_secret_key`) and then trusts `request.shop` to build `WebhookMetadata` passed to the app's handler: [3](#0-2) 

Contrast this with `Auth::Oauth::AuthQuery`, where `shop` is explicitly part of the signed string, correctly binding the identity to the HMAC: [4](#0-3) 

Because the app's `api_secret_key` (client secret) is shared across every shop that installs the app, a merchant who is a legitimate, unprivileged installer of a multi-tenant app can trigger a real webhook for their own store and capture a valid `(raw_body, hmac)` pair. Since the HMAC never covers the `shop` header, that same `(raw_body, hmac)` pair can be replayed directly against the app's webhook endpoint (not through Shopify's delivery infrastructure) with an arbitrary, attacker-chosen `x-shopify-shop-domain` header. `HmacValidator.validate` will still succeed because it only recomputes the HMAC over `raw_body`, and `Registry.process` will hand the handler a `WebhookMetadata` claiming the event came from an arbitrary victim shop — breaking the identity binding `shop authenticated == shop the HMAC actually vouches for`.

### Impact Explanation
This is a cross-tenant identity confusion: the gem lets an unprivileged installer make the host application believe arbitrary webhook data (order, customer, app/uninstalled, GDPR topics, etc.) originated from a different merchant's shop. Depending on how the host app uses `data.shop` (e.g., looking up that shop's stored access token/session, deleting data, revoking installation state, crediting orders), this can lead to cross-tenant data corruption or trigger privileged actions against a victim tenant, since the framework provides no verified linkage between the authenticated bytes (body) and the acted-upon identity (shop).

### Likelihood Explanation
Requires only that the attacker be a legitimate (even single) installer of the target multi-tenant app — no leaked secrets, no privileged account beyond ordinary app installation, and no MITM. They generate one genuine webhook for their own store (trivial, e.g. by placing a test order) to obtain a valid `(body, hmac)` pair, then POST it directly to the app's public webhook URL with a forged `shop-domain` header.

### Recommendation
Bind the shop domain (and ideally topic/webhook id) into the signed material, or otherwise verify that the shop present in the request corresponds to a shop for which the app can independently confirm receipt (e.g., cross-check against the shop that is expected to have sent this specific webhook subscription/topic), rather than trusting an arbitrary header once a body-only HMAC succeeds. At minimum, document prominently that `request.shop` is not authenticated by `HmacValidator.validate` and must not be used as a trust boundary without additional verification (e.g., matching against a known/installed shop list before processing).

### Proof of Concept
1. App installs on `attacker-shop.myshopify.com` (attacker is a normal merchant/customer of the app).
2. Attacker triggers a real webhook (e.g. `orders/create`) for their own shop and captures the raw POST body `B` and header `x-shopify-hmac-sha256: H`, where `H = HMAC-SHA256(api_secret_key, B)`.
3. Attacker sends a new POST directly to the app's webhook endpoint with body `B`, header `x-shopify-hmac-sha256: H` (unchanged), and `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` succeeds because it only checks `HMAC(secret, B) == H`. [5](#0-4) 
5. `Registry.process` invokes the app's handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the host application to act as though `victim-shop` sent this data.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
