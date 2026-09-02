### Title
Webhook shop identity (`WebhookMetadata#shop`) is trusted from an unauthenticated header while HMAC only covers the raw body - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook by validating only the raw request body against the HMAC signature, then hands the handler a `shop` value taken from the `X-Shopify-Shop-Domain` header, which is never included in the signed material. Any unprivileged party who can obtain one legitimately-signed webhook body/HMAC pair for the app (e.g. by installing the app on their own store) can replay that exact body with a forged shop-domain header, and the library will report it to the handler as originating from any other shop.

### Finding Description
`ShopifyAPI::Webhooks::Request` implements `Utils::VerifiableQuery`:

<cite repo="AYontt/shopify-api-ruby--006" path="lib/shopify_api/webhooks/request.rb" start="10-23" end="36-38" />

`hmac` is read from the `hmac-sha256` header, `shop` is read from the separate `shop-domain` header, but `to_signable_string` returns only `@raw_body`: [1](#0-0) 

`Utils::HmacValidator.validate` computes the HMAC exclusively over `to_signable_string` (i.e. the raw body) and compares it to the `hmac` header: [2](#0-1) 

`Registry.process` gates the whole webhook on that body-only HMAC check, then immediately builds `WebhookMetadata` using `request.shop` (an unverified header) and hands it to the host app's handler: [3](#0-2) 

`WebhookMetadata#shop` is a plain `String` field with no further verification and is the value host applications use to attribute the webhook to a specific merchant/tenant: [4](#0-3) 

The identity binding that should hold is:
`shop attributed to the event == shop that Shopify actually sent the event for`

Because the HMAC only signs `raw_body`, this equality is never checked. The `shop` field is fully attacker-controlled at the transport (HTTP header) layer, independent of whatever body/HMAC pair is replayed. This is a direct structural analog to the "kick_token doesn't respect the lock" bug class from the external report: the code path that is gated by an authenticity check (`kick_tokens` → `delist_internal`, here `process` → `handler.handle`) acts on a piece of state (`token`/`shop`) that the authenticity check does not actually cover.

Critically, in this gem the webhook HMAC secret (`Context.api_secret_key`, the app's `client_secret`) is a single, app-wide secret shared across every shop that installs the app — it is not shop-specific. This means:

1. An unprivileged internet user can install the target app on their own (attacker-controlled) development/trial store — a completely legitimate, low-privilege action requiring no special access.
2. Shopify will deliver real webhooks to the app's endpoint for that shop, each with a valid `X-Shopify-Hmac-Sha256` computed with the app's shared secret over the raw body.
3. The attacker captures one such `(raw_body, hmac)` pair.
4. The attacker (or any man-in-the-middle-free replay, e.g. via a proxy/browser tool since delivery endpoints are public HTTP(S) URLs) resends that exact body and HMAC to the app's webhook endpoint, but substitutes the `X-Shopify-Shop-Domain` header with an arbitrary victim shop domain (and optionally other headers such as `webhook-id`/`api-version`, also unauthenticated).
5. `HmacValidator.validate` succeeds because it only checks the body/HMAC pair, which is valid.
6. `Registry.process` calls the handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", ...)`, causing the host application to process/store data as if it originated from the victim tenant.

### Impact Explanation
This breaks the tenant/shop identity binding that every consumer of this gem's webhook feature relies on to route webhook data to the correct merchant record. Depending on how the host application uses `WebhookMetadata#shop` (nearly universal pattern: look up the merchant record/session by shop, then create/update/delete data, trigger mandatory-topic redaction flows, etc.), this enables cross-tenant data injection or manipulation — for example, triggering `shop/redact` or `customers/redact`/`customers/data_request` handling logic, or writing attacker-supplied "webhook" data into another merchant's records, purely by controlling the HTTP header of a replayed, already-validly-signed payload. This satisfies the "cross-tenant access" Critical impact category, since the binding between the app's own trusted secret (`client_secret`) and the shop it is presented as belonging to is not enforced anywhere in this gem.

### Likelihood Explanation
Likelihood is realistic and requires no privileged access:
- Installing an app on one's own shop is a normal, unprivileged action available to anyone.
- Webhook endpoints are public HTTP(S) URLs by design (Shopify must be able to reach them), so replaying a captured request with modified headers requires no special network position.
- No secret material needs to be recovered — the attacker's own shop naturally receives correctly-HMAC'd traffic they can freely inspect and replay, because the same `client_secret` is used for HMAC across all shops.
- The only constraint is that the replayed body must be a byte-for-byte match to a previously-signed body, which still allows meaningful attacks against handlers that act on topic/shop metadata without deeply validating body contents (e.g. mandatory compliance topics, or handlers that trust `data.shop` to select a tenant and only inspect specific safe fields of `data.body`).

### Recommendation
Bind the shop identity into the authenticity check, e.g. by including the `shop-domain` (and ideally `topic`, `webhook-id`) header values in the HMAC-signed material, or by cross-validating `request.shop` against an out-of-band trusted source (such as the currently active/stored session for that shop) before constructing `WebhookMetadata`. At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must not be used as a sole tenant-lookup key without additional verification.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com`.
2. Shopify delivers a legitimate webhook, e.g.:
   ```
   POST /webhooks HTTP/1.1
   X-Shopify-Topic: orders/create
   X-Shopify-Hmac-Sha256: <valid-hmac-for-body>
   X-Shopify-Shop-Domain: attacker-shop.myshopify.com
   X-Shopify-Webhook-Id: ...

   {"id": 123, ...}
   ```
3. Attacker replays the exact same body and `X-Shopify-Hmac-Sha256` value to the app's webhook endpoint, but sets:
   ```
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   ```
4. `ShopifyAPI::Webhooks::Request.new(raw_body:, headers:)` parses this successfully (`shop` returns `"victim-shop.myshopify.com"`), and `Utils::HmacValidator.validate(request)` returns `true` because it only checks `raw_body` against the reused, valid HMAC — see `lib/shopify_api/webhooks/request.rb` lines 10-38 and `lib/shopify_api/utils/hmac_validator.rb` lines 12-31.
5. `Registry.process` invokes the host app's handler with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", topic: "orders/create", body: {...})` (`lib/shopify_api/webhooks/registry.rb` lines 188-200), causing the application to act on data attributed to the victim shop.

### Citations

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
