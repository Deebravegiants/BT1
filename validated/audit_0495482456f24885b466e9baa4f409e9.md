## Finding [1](#0-0) 

### Title
Webhook shop-domain identity spoofing via HMAC scope mismatch (`shop` header not covered by signature) - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable signable string from only the raw request body [2](#0-1) , while the tenant-identifying `shop` value used downstream is read from the unsigned `shopify-shop-domain`/`x-shopify-shop-domain` HTTP header [3](#0-2) . `Webhooks::Registry.process` validates the request's HMAC (over the body only) and then forwards `request.shop` straight into `WebhookMetadata` as the authenticated tenant identifier, without the HMAC ever covering that field [4](#0-3) .

### Finding Description
The equality that should hold is: `shop attested by the cryptographic signature == shop used to attribute/process the webhook payload`. Here it does not: the HMAC only binds the request body, so `hmac(secret, raw_body)` says nothing about the `shop-domain` header. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which internally calls `request.to_signable_string`, returning `@raw_body` alone [2](#0-1)  and [5](#0-4) . Immediately after validation succeeds, `request.shop` (the raw header value) is passed unmodified into the handler as the shop of record [6](#0-5) .

Because a merchant who has installed the app is a legitimate recipient of their own webhooks (with a valid body+HMAC pair for their own shop), they can capture that authentic `(raw_body, hmac)` pair and replay it to the app's webhook endpoint while substituting an arbitrary `shopify-shop-domain` header value (e.g., a victim shop's domain). `HmacValidator.validate` still succeeds because the header is not part of the signed material, yet the app will process/attribute the (attacker's own, but now mislabeled) webhook payload as if it originated from the victim shop.

### Impact Explanation
This crosses a tenant boundary: the gem hands the host application a "verified" `WebhookMetadata` object whose `shop` field is actually unauthenticated. Any consumer application that uses `WebhookMetadata#shop` to key data (e.g., to select which shop's records to update, or to satisfy GDPR `shop/redact`/`customers/redact` mandatory webhooks) can be made to act on/for the wrong tenant — a cross-tenant data confusion driven entirely by the gem's own signature scope, matching the report's "field acted on but not covered by the HMAC" bug class.

### Likelihood Explanation
Exploitation only requires an actor who is already a legitimate recipient of at least one authentic webhook for their own shop (i.e., any app-installing merchant) — no access to `api_secret_key` is needed, since they simply replay a body+HMAC pair they legitimately received and change the header value. This satisfies the "unprivileged internet user" bar of the rules.

### Recommendation
Include the shop domain (and ideally topic/webhook-id) as part of the signed material verified against the HMAC, or otherwise cryptographically bind the header values to the signature before trusting them in `WebhookMetadata`. At minimum, document/enforce that `request.shop` must not be treated as verified merely because `HmacValidator.validate` passed.

### Proof of Concept
1. Attacker installs the target app on `attacker-shop.myshopify.com` and triggers/receives a legitimate webhook with body `B` and header `X-Shopify-Hmac-Sha256: H` (valid for `B` under the shared secret).
2. Attacker POSTs to the app's webhook endpoint with the same body `B` and same `X-Shopify-Hmac-Sha256: H`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
3. `Registry.process` calls `HmacValidator.validate(request)`, which passes because it only checks `hmac(secret, B) == H` [7](#0-6) .
4. `WebhookMetadata.new(..., shop: request.shop, ...)` is built with `shop == "victim-shop.myshopify.com"` [8](#0-7) , and the host app's handler processes the attacker-controlled payload `B` as if it came from the victim shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L10-38)
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
