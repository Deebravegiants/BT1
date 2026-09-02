### Title
Webhook `shop`, `topic`, and `webhook_id` are trusted metadata not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`, `lib/shopify_api/webhooks/registry.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` treats a webhook as authenticated once `Utils::HmacValidator.validate(request)` returns true, then hands the caller a `WebhookMetadata` built from `request.shop`, `request.topic`, and `request.webhook_id`. However, the HMAC signature only covers the raw request body — none of `shop`, `topic`, or `webhook_id` are part of the signed data. An attacker who possesses any single genuinely-signed `(raw_body, hmac)` pair (trivially obtainable by installing the public app on their own, attacker-controlled shop) can replay that pair while substituting the `shopify-shop-domain` (and `shopify-topic`/`shopify-webhook-id`) headers, producing a request that passes HMAC validation yet is falsely attributed to an arbitrary victim shop and/or topic.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

Meanwhile `shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers, which are never mixed into the signed string: [2](#0-1) 

`Registry.process` validates the request solely via `HmacValidator.validate`, then blindly forwards the header-derived `shop`/`topic`/`webhook_id` to the app's handler as trusted metadata: [3](#0-2) 

`HmacValidator.validate` computes the HMAC only over `verifiable_query.to_signable_string`, i.e., the raw body, and compares it against the received `hmac-sha256` header: [4](#0-3) 

The intended identity binding is:
`valid_hmac(raw_body, secret) == true` **⇒** `(shop, topic, webhook_id, raw_body)` all genuinely originated together from Shopify for that specific tenant.

The actual binding implemented is only:
`valid_hmac(raw_body, secret) == true` **⇒** `raw_body` was signed by *some* legitimate Shopify webhook delivery (to *any* shop that installed the app) — `shop`, `topic`, and `webhook_id` are unauthenticated header values an attacker fully controls.

Since a public/unprivileged attacker can install the app on their own store and legitimately receive at least one signed webhook (any topic, any body), they capture a valid `(raw_body, shopify-hmac-sha256)` pair. They then replay this exact body/signature to the app's webhook endpoint while freely rewriting `shopify-shop-domain` to a victim's `*.myshopify.com` domain (and/or `shopify-topic` to a different registered topic string, e.g. one of the mandatory GDPR topics `shop/redact`, `customers/redact`, `customers/data_request`). `Registry.process` will still consider the request validly HMAC-authenticated and dispatch it to the handler with `WebhookMetadata#shop` pointing at the victim shop.

### Impact Explanation
This breaks the tenant-identity binding that host applications rely on when consuming this gem's documented webhook API (`WebhookMetadata#shop`/`#topic`). An app that uses `shop` from a "validated" webhook to select which tenant's data/session to act on (e.g., mandatory compliance handlers for `shop/redact`, `customers/redact`, `customers/data_request`) can be tricked into performing tenant-scoped actions attributed to a shop that never sent that data — a cross-tenant confusion/spoofing condition. This matches the report's "Critical – cross-tenant access" category, since the HMAC check gives false assurance that the shop/topic pairing is authentic when it is not.

### Likelihood Explanation
Any internet user can become a legitimate (if low-privilege) installer of a public Shopify app to harvest one valid `(raw_body, hmac)` pair for their own shop, then immediately reuse it against the app's public webhook endpoint with a forged `shopify-shop-domain` header — no access token, `client_secret`, or privileged account is required. The only constraint is that the replayed body content is fixed to whatever was originally signed, but topic/shop/webhook_id are fully forgeable, making this straightforward to exploit for topic/tenant confusion attacks.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the signed/verifiable string (or otherwise cryptographically bind them to the HMAC), so that `HmacValidator.validate` fails if any of these header-derived fields are altered relative to what Shopify actually signed for that specific delivery.

### Proof of Concept
1. Attacker installs the target public app on their own store `attacker.myshopify.com` and lets it receive one legitimate webhook, capturing the raw POST body `B` and the `X-Shopify-Hmac-Sha256: H` header Shopify sent.
2. Attacker sends a forged HTTP POST to the app's webhook endpoint with:
   - Body: the exact same bytes `B`
   - Headers: `X-Shopify-Hmac-Sha256: H` (unchanged, still valid because body `B` is unchanged), `X-Shopify-Shop-Domain: victim.myshopify.com` (forged), `X-Shopify-Topic: customers/redact` (forged, if different from original topic and app registered a handler for it).
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: forged_headers)` builds a request object; `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes HMAC over `B` only and matches `H` — validation succeeds.
4. The registered handler for `customers/redact` is invoked with `WebhookMetadata.new(shop: "victim.myshopify.com", topic: "customers/redact", body: JSON.parse(B), ...)`, causing the app to perform a tenant-scoped action attributed to `victim.myshopify.com` even though `victim.myshopify.com` never sent this webhook.

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
