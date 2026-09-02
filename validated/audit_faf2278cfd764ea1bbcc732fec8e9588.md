### Title
Cross-tenant webhook impersonation — `shop` header is not covered by the HMAC signature - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating an HMAC over the raw request body, then trusts the unsigned `shop-domain` header as the tenant identifier that gets handed to the app's business logic. Because the shop identity is never bound into the signed bytes, any two shops served by the same app share one HMAC key and can produce mutually-valid `(body, hmac)` pairs, letting a webhook that is cryptographically valid for shop A be replayed with the header claiming to be shop B.

### Finding Description
`Webhooks::Request` implements `Utils::VerifiableQuery` and defines the signable content as only the raw body: [1](#0-0) 

`shop`, `topic`, `webhook_id`, and `api_version` are all read straight from HTTP headers and are **not** part of `to_signable_string`: [2](#0-1) 

`HmacValidator.validate` only checks `verifiable_query.hmac` against `compute_signature(verifiable_query.to_signable_string, secret)` — i.e. it authenticates the body bytes against a single, app-wide `api_secret_key`, never the shop identity: [3](#0-2) 

`Registry.process` then uses the *unsigned* `request.shop` value directly as the tenant identifier passed to the handler: [4](#0-3) 

The binding that should hold is:
`shop_the_HMAC_authenticates == shop_the_handler_acts_on`

but the actual equality enforced is only:
`HMAC(body, api_secret_key) == received_hmac`

with `shop` free-floating in an unsigned header. Since `api_secret_key` is a single shared secret across every shop that has installed the app (not a per-shop key), a legitimately-signed body originating from *shop A*'s webhook traffic remains valid if resent with the `shopify-shop-domain` (or `x-shopify-shop-domain`) header changed to *shop B*. `WebhookMetadata.shop` — the value the app-supplied `handler.handle` block uses to decide which tenant's records to update — is populated straight from that header: [5](#0-4) 

### Impact Explanation
This breaks the shop/tenant isolation boundary the gem is expected to enforce for webhook processing. A user who legitimately installs the app on their own store (an "unprivileged" shop owner from the target application's perspective — no special access to the target tenant's system) can capture one valid `(raw_body, hmac)` pair delivered to the app for their own shop, then replay that exact payload to the app's public webhook endpoint with a forged `shop-domain`/`x-shopify-shop-domain` header naming a different shop. `Registry.process` will accept it (HMAC still matches, since the body was unmodified) and dispatch it to the handler as if it originated from the victim shop, causing the host application to write/mutate/act on data keyed to the wrong tenant — a cross-tenant integrity/confidentiality violation. This satisfies the "cross-tenant access" criterion for a Critical/High-impact finding, and requires no possession of `api_secret_key`, access tokens, or TLS interception — only observation of one's own legitimately delivered webhook traffic (e.g., via a local ngrok/ tunnel logging proxy, which any merchant/developer can set up for their own shop).

### Likelihood Explanation
Likelihood is moderate: the attacker needs (a) their own working installation of the target app (trivial — many apps are self-serve installable), and (b) the ability to observe the raw bytes of one webhook delivered to their own tunnel/endpoint, which is standard for anyone developing/debugging against their own installation. No cryptographic secret needs to be recovered — only replay of an already-valid signature with a different (unsigned) header value.

### Recommendation
Bind the tenant identity into the authenticated bytes, or otherwise cryptographically tie the header-supplied `shop` to the signed payload before trusting it: e.g., include `shop-domain` in `to_signable_string`, or verify that the `shop` field present in the parsed JSON body (`admin_graphql_api_id`/`myshopify_domain` fields Shopify includes in most payloads) matches the header-supplied shop before invoking the handler. At minimum, document/enforce that host applications must cross-check `WebhookMetadata.shop` against a previously known/registered shop before trusting it for tenant-scoped writes, since the library provides no such binding today.

### Proof of Concept
1. Install the target Shopify app on an attacker-controlled shop `attacker.myshopify.com`, with the webhook delivery endpoint pointed at a local reverse proxy/tunnel the attacker controls.
2. Trigger any subscribed webhook event (e.g., `orders/create`) on the attacker's own shop; capture the exact raw body and the `X-Shopify-Hmac-Sha256`/`shopify-hmac-sha256` header Shopify sent — this pair is valid under the app's single `api_secret_key`.
3. Send an HTTP POST directly to the app's public webhook endpoint reusing that captured `raw_body` and `hmac` header unchanged, but replace the `shopify-shop-domain` (or `x-shopify-shop-domain`) header with `victim-shop.myshopify.com`.
4. `Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which only checks `HMAC(raw_body, api_secret_key) == hmac` — this still passes because the body/hmac pair is untouched: [6](#0-5) 
5. The handler is invoked with `WebhookMetadata.new(... shop: request.shop ...)` where `request.shop` now equals `"victim-shop.myshopify.com"`, causing the host app to process the attacker's forged event as if it belongs to the victim tenant.

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
