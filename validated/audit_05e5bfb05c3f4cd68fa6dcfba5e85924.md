### Title
Webhook `shop` (and `topic`/`webhook_id`) identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` derives the tenant identifier (`shop`), `topic`, and `webhook_id` from unauthenticated HTTP headers, while the HMAC signature that `ShopifyAPI::Webhooks::Registry.process` validates is computed **only over the raw request body**. Because the app's `api_secret_key` is shared across every merchant/shop that has installed the app, any party that legitimately receives one valid `(body, hmac)` pair for the app (e.g., a merchant who has installed the app and receives genuine webhooks to their own endpoint, or anyone who can observe one webhook delivery) can replay that exact body/HMAC pair while substituting an arbitrary `shopify-shop-domain` header. The signature still validates, and the app's webhook handler is invoked believing the payload belongs to a different, spoofed shop — a violation of the binding "shop authenticated == shop the data is attributed to."

### Finding Description
`Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop`, `topic`, and `webhook_id` accessors are pulled straight from headers that are never fed into the signed string: [2](#0-1) 

`Webhooks::Registry.process` validates the request purely via `Utils::HmacValidator.validate(request)`, which calls `request.to_signable_string` (the raw body) and compares against the app's shared `Context.api_secret_key`: [3](#0-2) [4](#0-3) 

Once validation succeeds, `request.shop` (fully attacker-controlled, unauthenticated) is handed directly to the registered handler as the tenant identifier: [5](#0-4) 

The equality the system is supposed to guarantee is:
`shop authenticated by the HMAC == shop attributed to the webhook payload delivered to the handler`

Because the signed bytes are only the body, and the shop domain/topic/webhook id live outside the signed bytes, this equality does not hold. Any holder of one valid `(raw_body, hmac)` pair for the app (obtainable by simply being a merchant who installed the app, since `api_secret_key` is one shared secret across all of the app's shops) can resubmit that same body/HMAC with a different `shopify-shop-domain` header value and have it accepted as authentic data for an arbitrary victim shop.

### Impact Explanation
This breaks tenant isolation (cross-tenant access/confusion) for any host application that relies on this gem's `Webhooks::Registry.process`/`Request` to authenticate which shop a webhook payload belongs to. A malicious/unprivileged app installer can:
- Spoof `app/uninstalled` or similar lifecycle webhooks against another tenant, causing the host app to deprovision or corrupt an unrelated shop's stored data.
- Inject attacker-controlled resource payloads that get attributed and persisted under another shop's identity in the host application's datastore.

This matches the "cross-tenant access" Critical impact category since it crosses a tenant boundary using only a signature that was never meant to authenticate the tenant field it is used to gate.

### Likelihood Explanation
Likelihood is realistic: any actor who has installed the app on their own shop (a normal, unprivileged install — no `api_secret_key`, no stolen tokens, no TLS interception needed) automatically receives genuine `(body, hmac)` pairs from Shopify for their own shop's events, since the secret is shared across the whole app rather than per-shop. That same actor can trivially POST the identical body/HMAC to the app's public webhook endpoint with a forged `shopify-shop-domain` header naming a different victim shop.

### Recommendation
Bind the shop (and ideally topic/webhook_id) into the signed material, or otherwise cryptographically tie the header-derived shop to the request that was HMAC-validated — e.g., require the host application to cross-check `request.shop` against a shop known to be associated with the specific `webhook_id`/subscription that was registered for that shop, rather than trusting the header value once the body-only HMAC passes. At minimum, document prominently that `request.shop` is unauthenticated by `HmacValidator.validate` and must be independently verified (e.g., against the app's own installed-shop records) before being used as a tenant/session key.

### Proof of Concept
1. Install the target app on shop `attacker.myshopify.com`; Shopify sends a legitimate webhook, e.g. `orders/create`, with body `B` and header `x-shopify-hmac-sha256: H` (computed over `B` using the app's single shared `api_secret_key`).
2. Attacker captures `(B, H)` from their own legitimate webhook delivery (or from proxying their own traffic — no special access needed).
3. Attacker crafts a new HTTP POST to the app's webhook endpoint with the same body `B` and same `x-shopify-hmac-sha256: H` header, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
4. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(B, api_secret_key) == H` — this passes because `B` and `H` are unchanged.
5. The handler executes with `data.shop == "victim-shop.myshopify.com"`, processing attacker-supplied data under the victim's tenant identity. [3](#0-2)

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

**File:** lib/shopify_api/webhooks/request.rb (L35-43)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
      end

      sig { returns(T::Hash[String, T.untyped]) }
      def parsed_body
        JSON.parse(@raw_body)
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
