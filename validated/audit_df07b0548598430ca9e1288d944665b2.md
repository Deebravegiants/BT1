### Title
Webhook `shop-domain` header is not covered by the HMAC signature, enabling cross-tenant webhook forgery - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identifier (`shop`) from the `x-shopify-shop-domain` HTTP header, but the HMAC signature validated by `ShopifyAPI::Utils::HmacValidator` only covers the raw request body (`to_signable_string` returns `@raw_body`). Because Shopify webhook HMACs are computed with the app's single, shop-independent `api_secret_key`, a valid `(raw_body, hmac)` pair obtained from one shop's legitimate webhook delivery remains valid when replayed with a different, attacker-chosen `shop-domain` header. This breaks the intended equality `shop authenticated == shop the signed payload actually originated from`, allowing an unprivileged attacker who controls their own installed shop to make the app process forged data attributed to a victim shop.

### Finding Description
`Request#hmac` and `Request#to_signable_string` only expose the raw HTTP body for signature verification: [1](#0-0) 

`Request#shop` is read straight from the `shopify-shop-domain` / `x-shopify-shop-domain` header, which is never part of the signed material: [2](#0-1) 

`Registry.process` validates the HMAC solely via `Utils::HmacValidator.validate(request)`, and — once it passes — hands the handler a `WebhookMetadata` built from `request.shop`, i.e. the unauthenticated header value: [3](#0-2) 

`HmacValidator.validate` computes/compares the signature only against `verifiable_query.to_signable_string` (the raw body) using the app's `api_secret_key`: [4](#0-3) 

Crucially, Shopify webhook HMACs are computed with the **app's** `api_secret_key`, which is identical for every shop that installs the app — it is not a per-shop secret. This means the signature only proves "this body byte-stream was produced by Shopify for *some* installation of our app," not "this body belongs to *this specific* shop." The binding the code implicitly assumes:

```
shop the handler processes as == shop that produced/authorized this signed body
```

does not hold, because the `shop` value is taken from an unsigned header while the signature only covers the body.

### Impact Explanation
Impact: **Cross-tenant access** (High, per the given severity classes).

An attacker who installs the vulnerable app on their own shop (a completely normal, unprivileged action) can:
1. Trigger a webhook event on their own shop, causing Shopify to deliver a webhook to the app's endpoint with a real `raw_body` + `x-shopify-hmac-sha256` pair signed with the app's shared `api_secret_key`.
2. Capture that `(raw_body, hmac)` pair (it is delivered to the attacker's own controlled infrastructure/proxy in front of the app, or logged by the attacker's own shop's webhook subscription endpoint if they can observe it).
3. Replay the exact same `raw_body` and `hmac` header to the app's webhook endpoint, but substitute the `x-shopify-shop-domain` header with the victim shop's domain.
4. `HmacValidator.validate` succeeds (it only checks the body), and `Registry.process` invokes the app's webhook handler with `WebhookMetadata#shop` set to the victim shop, even though the payload content originated from the attacker's shop.

Depending on how the host application uses `WebhookMetadata#shop` (e.g., to look up the victim's session/access token and act on the victim's store data, update local records keyed by shop, or trigger side effects scoped to the victim tenant), this allows the attacker to inject attacker-controlled data into the victim's tenant context — a direct cross-tenant boundary break rooted in this gem's webhook request/verification code.

### Likelihood Explanation
Likelihood is realistic for any Shopify app that installs across multiple independent merchants (the standard SaaS app model), because:
- Any attacker can freely install the app on their own shop (no special privilege required — this is exactly the "unprivileged internet user" scenario).
- Obtaining a valid `(body, hmac)` pair requires no secret knowledge; it's simply capturing your own legitimately delivered webhook.
- The `api_secret_key` is shared across all shops using the app, so the same signature validates regardless of which shop's domain header accompanies the replayed body — this is inherent to how the gem implements the check, not a hypothetical scenario.
- There is no nonce/timestamp/shop binding check in `HmacValidator`/`Request` that would prevent this cross-tenant replay (no `webhook-id` uniqueness enforcement, no shop-scoped signature check).

### Recommendation
Bind the `shop` (and ideally `webhook-id`) to the same trust boundary as the signature:
- Compute/verify the HMAC over a signable string that includes the `shop-domain` header (and other identifying headers) in addition to the raw body, so tampering with the shop header invalidates the signature.
- Alternatively/additionally, if the app maintains its own per-shop mapping (installed shop list), cross-check the `shop-domain` header value against `Utils::ShopValidator` and reject/require a secondary matching signal (e.g., a per-shop secret or a lookup that ties the delivered `webhook-id`/topic pairing to shop registration) before trusting `WebhookMetadata#shop`.
- At minimum, document prominently that `WebhookMetadata#shop` is NOT covered by the HMAC and must not be trusted for tenant attribution without additional verification by the host application.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com`.
2. Attacker triggers any webhook topic the app subscribes to (e.g., `orders/create`) with attacker-controlled body content, letting Shopify deliver it with a legitimate signature:
   ```
   POST /webhooks
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <valid-signature-for-body>
   x-shopify-shop-domain: attacker-shop.myshopify.com
   x-shopify-webhook-id: <id>

   { ...attacker-controlled body... }
   ```
3. Attacker captures the exact raw body and `x-shopify-hmac-sha256` value.
4. Attacker replays the identical body/hmac to the same endpoint but swaps the shop header:
   ```
   POST /webhooks
   x-shopify-topic: orders/create
   x-shopify-hmac-sha256: <same-valid-signature-for-body>
   x-shopify-shop-domain: victim-shop.myshopify.com
   x-shopify-webhook-id: <id>

   { ...same attacker-controlled body... }
   ```
5. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which returns `true` because the signature is checked only against `raw_body` [5](#0-4) . The handler is then invoked with `shop: request.shop == "victim-shop.myshopify.com"` [6](#0-5) , giving the attacker's forged payload the victim shop's tenant identity.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-43)
```ruby
      sig { override.returns(String) }
      def hmac
        Digest.hexencode(Base64.decode64(T.cast(shopify_header("hmac-sha256"), String)))
      end

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

      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-40)
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

        sig { params(signable_string: String, secret: String).returns(String) }
        def compute_signature(signable_string, secret)
          OpenSSL::HMAC.hexdigest(
            OpenSSL::Digest.new("sha256"),
            secret,
            signable_string,
          )
        end
```
