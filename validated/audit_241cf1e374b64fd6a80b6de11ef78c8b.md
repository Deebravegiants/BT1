### Title
Webhook tenant (`shop`) and `topic` are trusted from unauthenticated HTTP headers while the HMAC only covers the raw body, enabling cross-tenant webhook spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates a webhook delivery solely by validating an HMAC over the raw request body, then dispatches to the app's handler using the `shop`, `topic`, `webhook_id`, and `api_version` values taken directly from unauthenticated HTTP headers. Because those header fields are never included in the HMAC-signed string, an attacker who can obtain any single validly-signed `(raw_body, hmac)` pair for their own tenant (e.g. by installing the app on a shop they control) can replay that exact body/HMAC to the app's public webhook endpoint while substituting the `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`) header for an arbitrary victim shop. The HMAC check still passes because it never covered those header fields, and the handler is invoked believing the event originated from the victim tenant.

### Finding Description
`ShopifyAPI::Webhooks::Request` derives its signable content only from the raw body: [1](#0-0) 

and the fields used to route/identify the tenant (`shop`, `topic`, `webhook_id`, `api_version`) are pulled straight from headers with no cryptographic binding to the signed payload: [2](#0-1) 

`HmacValidator.validate` only ever checks `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)`, i.e. against the raw body string, never against `shop`/`topic`/`webhook_id`: [3](#0-2) 

`Registry.process` uses this HMAC check as the sole authentication gate, and then constructs the `WebhookMetadata` object passed to the app's handler directly from the unauthenticated `request.shop` / `request.topic` / `request.webhook_id` values: [4](#0-3) 

The identity binding that should hold is: `shop-attributed-to-webhook == shop-that-produced-the-signed-bytes`. Because the signed bytes are only the body, and the shop attribution comes from a header outside that signature, this equality is not enforced — the shop label can be swapped for any value while keeping a valid signature computed over unrelated content.

### Impact Explanation
An attacker who has legitimate but unprivileged access to any single shop (their own development/test store, requiring no special credentials, access tokens, or `api_secret_key` knowledge) can install the target app, capture one of the genuine webhook deliveries Shopify sends them (raw body + valid `X-Shopify-Hmac-Sha256`), and replay that exact request to the app's public webhook endpoint with the `X-Shopify-Shop-Domain` header changed to an arbitrary victim shop domain. `Registry.process` will accept it as authentic (HMAC still validates) and invoke the app's webhook handler as if the event belonged to the victim tenant. Depending on how the host application implements its handler (e.g. `app/uninstalled`, `shop/redact`, `customers/data_request`, billing/plan-change webhooks, or any handler that mutates per-shop state keyed by `data.shop`), this allows cross-tenant state corruption, forged uninstall/redact/GDPR events against a shop the attacker doesn't own, or triggering business logic against another merchant's data — a cross-tenant access impact.

### Likelihood Explanation
Likelihood is meaningful but not trivial: the attacker needs (a) an app installed on any shop they control (freely available to any developer), (b) the ability to capture at least one real webhook delivery to that shop (straightforward — they control the receiving endpoint or can proxy/log it), and (c) knowledge/guessability of a target victim shop's `.myshopify.com` domain (public information for most stores). No possession of the app's `client_secret`, access tokens, or any privileged credential is required, which keeps this in-scope of an unprivileged-internet-user threat model.

### Recommendation
Bind the tenant/topic identity into the authenticated material instead of trusting bare headers:
- Include `shop`, `topic`, and `webhook_id` in the HMAC-signed/verified string (or otherwise cryptographically bind them), so any substitution invalidates the signature, matching how `AuthQuery#to_signable_string` binds all OAuth callback fields.
- Alternatively, require applications to independently verify that `request.shop` corresponds to a shop with an active, previously-established session/installation before acting on webhook data, rather than trusting the header value implicitly.
- Reject webhook deliveries where the `topic` header doesn't match a topic the registered webhook subscription actually expects for that specific shop's known webhook_id.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` (a shop they legitimately control) and lets it register a webhook (e.g. `orders/create`).
2. Shopify delivers a real webhook to the app's endpoint with headers including a valid `X-Shopify-Hmac-Sha256` computed over the raw body using the app's shared secret, and `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`.
3. Attacker captures this exact raw body and HMAC value (they control the endpoint/proxy receiving it).
4. Attacker replays the identical HTTP POST (same raw body, same HMAC header) directly to the app's public webhook endpoint, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
5. Server-side, `ShopifyAPI::Webhooks::Request.new` parses the spoofed header, and `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which passes because it only checks the (unchanged) raw body against the (unchanged) HMAC: [5](#0-4) 
6. The app's registered handler executes with `data.shop == "victim-shop.myshopify.com"`, even though the underlying payload and signature were produced by/for the attacker's own shop — a full tenant-identity mismatch that the gem does not detect or prevent.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-38)
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
