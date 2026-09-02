Confirmed root cause: `Webhooks::Request#to_signable_string` returns only `@raw_body` [1](#0-0) , while `shop` (and `topic`, `webhook_id`, `api_version`) are read from unauthenticated HTTP headers via `shopify_header` [2](#0-1) [3](#0-2) . `Registry.process` validates the HMAC over the body only via `Utils::HmacValidator.validate(request)`, then immediately passes `request.shop` into `WebhookMetadata` and to the app's handler without the shop being covered by that signature [4](#0-3) .

### Title
Webhook tenant identity (`shop-domain`) is not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes the HMAC signature over the raw request body only, but the `shop` field — used by `Registry.process` to build `WebhookMetadata` and dispatch to the host app's handler — is taken from the unauthenticated `X-Shopify-Shop-Domain` header. Because the app's `api_secret_key` is shared across every shop that installs the app, any shop can obtain a validly-signed webhook body from Shopify for its own store and replay it to the app's webhook endpoint with a forged `shop-domain` header pointing at a victim tenant, since only the body bytes (not the header) are checked against the signature.

### Finding Description
`Request#hmac` and `Request#to_signable_string` are defined so that `HmacValidator.validate` verifies the HMAC exclusively against `@raw_body`: [5](#0-4) [1](#0-0) 

`shop` is a plain header read, entirely outside the signed material: [2](#0-1) 

`HmacValidator.validate` computes the signature purely from `to_signable_string` (the body) and compares it to the received HMAC, with no reference to the shop header at all: [6](#0-5) 

`Registry.process` raises only if the HMAC fails, then trusts `request.shop` (i.e., the unauthenticated header) to build `WebhookMetadata` and invoke the app's handler: [4](#0-3) 

The identity binding that should hold is: `shop that is HMAC-authenticated == shop that the handler acts on`. Because the signature is computed over `raw_body` alone, this equality is not enforced — the signature only proves "this body byte sequence was produced by the app's secret," not "this body belongs to shop X." Any tenant that legitimately installs the app receives real webhooks from Shopify (signed with the same shared `api_secret_key` used for all shops of that app), and can capture the `raw_body` + valid `hmac-sha256` header from their own genuine delivery, then replay that exact body/HMAC pair to the app's webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` (or `shopify-shop-domain`) header for a different, victim shop domain. `Request` will parse the forged header as `shop`, `HmacValidator.validate` will still pass (body unchanged), and `Registry.process` will hand `WebhookMetadata.new(shop: <forged-shop>, ...)` to the host application's handler as if Shopify genuinely sent that payload for the victim shop.

### Impact Explanation
This crosses a tenant boundary using only unprivileged capability (installing the app on one's own shop, which is the normal, expected way any merchant interacts with the app) to inject attacker-controlled webhook data attributed to a different shop. Any host application that relies on `WebhookMetadata#shop` to select which tenant's records to create/update/delete (a documented, intended use per `docs/usage/webhooks.md`) can be made to write or act on data under a victim shop's identity, i.e., cross-tenant access/injection, satisfying the "Critical - cross-tenant access" impact bar.

### Likelihood Explanation
Likelihood is high for any app that has more than one installing shop: obtaining a legitimately-signed webhook body/HMAC pair requires nothing more than installing the app on an attacker-owned store (which triggers real Shopify webhook deliveries), and forging the shop-domain header on the replayed HTTP request is trivial since the header is never bound to the signature.

### Recommendation
Include the shop domain (and ideally topic/webhook-id/api-version) in the signable string / signature computation, or otherwise cryptographically bind the shop identity to the payload before trusting it (e.g., verify the shop against an independently-established session/webhook registration record rather than the raw header) in `Webhooks::Request#to_signable_string` and `Registry.process`.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`, triggering a real Shopify webhook delivery signed with the app's shared `api_secret_key`; attacker captures the raw body `B` and the `X-Shopify-Hmac-Sha256` header value `H` from that request (`H` is valid for `B` per `Request#hmac`/`HmacValidator.validate`, see [5](#0-4)  and [7](#0-6) ).
2. Attacker sends a new POST to the app's webhook endpoint with the same body `B` and same `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` parses `shop` from the forged header [2](#0-1) ; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks `B` against `H` [8](#0-7) .
4. The host app's `WebhookHandler#handle` receives `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: <attacker's data>, ...)` [9](#0-8) , and — if it trusts `data.shop` for tenant scoping as the gem's own documentation encourages — processes attacker-controlled data as if it belonged to the victim shop, achieving cross-tenant data injection.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-13)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end
```

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
