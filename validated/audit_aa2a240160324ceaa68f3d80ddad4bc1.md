### Title
Webhook Shop/Topic Identity Not Bound to HMAC Signature Enables Cross-Tenant Webhook Spoofing - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
The reported "hardcoded slippage" issue is a DeFi contract bug and doesn't apply directly, but its underlying bug class — a value that is trusted/acted upon without being covered by the security check that is supposed to validate it — maps onto a real identity-binding gap in this gem's webhook processing. `ShopifyAPI::Webhooks::Request` signs only the raw HTTP body with the app's `client_secret`-derived HMAC, while the `shop`, `topic`, `api-version`, and `webhook-id` values used to route and attribute the webhook to a tenant come from unauthenticated HTTP headers.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

But `shop`, `topic`, `api_version`, and `webhook_id` are all pulled straight from HTTP headers with no cryptographic binding to the signed payload: [2](#0-1) 

`Utils::HmacValidator.validate` only proves that `HMAC(api_secret_key, raw_body) == received_hmac`; it never inspects or binds the `shop-domain`, `topic`, `webhook-id`, or `api-version` headers: [3](#0-2) 

`Registry.process` accepts the request once this body-only HMAC check passes, then dispatches the handler using the *header-derived* `request.shop`, `request.topic`, and `request.webhook_id` as the trusted tenant/topic identity: [4](#0-3) 

The equality the HMAC is supposed to guarantee is: `hmac_valid ⇒ (raw_body, shop, topic) all authentic for this request`. In reality it only guarantees `hmac_valid ⇒ raw_body authentic`. `shop`, `topic`, `webhook_id`, and `api_version` are unauthenticated bytes that ride along in headers outside the signed scope.

### Impact Explanation
Because the shop identity is not covered by the signature, any entity capable of triggering (or previously capturing) one legitimately-signed webhook body/HMAC pair — for example, a developer who installs the same app on their own store and receives a real webhook for a given topic — can replay that exact `raw_body` + `hmac` pair to the app's webhook endpoint while substituting an arbitrary `X-Shopify-Shop-Domain` (and/or `X-Shopify-Topic`/`X-Shopify-Webhook-Id`) header. `Utils::HmacValidator.validate` will still return `true` because it only re-derives the HMAC from `raw_body`. The host application's webhook handler then processes/persists that payload as belonging to the spoofed shop, breaking the shop-to-payload identity binding and enabling cross-tenant data injection/attribution — the same class of unprivileged internet-facing "field acted on but not covered by the HMAC" bug called out in the review rules.

### Likelihood Explanation
Exploitation requires no possession of `api_secret_key`, no access token, and no privileged account — only one previously-observed authentic (body, HMAC) pair for any topic the attacker is legitimately entitled to receive (trivial to obtain by installing a public app on a free/dev store, or observing any webhook delivery). The attacker only needs to change plain HTTP headers on the replay request, since `ShopifyAPI::Webhooks::Request` and `HmacValidator` never re-verify header consistency with the signed body.

### Recommendation
Bind the identity fields into the signed material actually verified, or otherwise cryptographically/contextually verify them:
- Cross-check the `shop-domain` header against an independently known, previously-registered shop for the specific `webhook-id`/topic before dispatch, rather than trusting the header value verbatim.
- Where possible, validate that the shop domain in the header is consistent with data embedded in `raw_body` (Shopify webhook payloads typically also carry shop-identifying fields), and reject on mismatch.
- Document clearly (and enforce where feasible) that consuming applications must not use `WebhookMetadata#shop` as the sole tenant-authentication input without additional server-side authorization checks tying it back to a known session/store record.

### Proof of Concept
1. Attacker installs the target app on their own store `attacker.myshopify.com` and triggers a webhook (e.g. `orders/create`) they are entitled to receive, capturing the raw POST body and the `X-Shopify-Hmac-Sha256` header Shopify sent.
2. Attacker resends the exact same body and HMAC header to the app's webhook endpoint, but replaces:
   - `X-Shopify-Shop-Domain: victim-shop.myshopify.com`
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(api_secret_key, raw_body)` and finds it matches the replayed header — validation succeeds: [5](#0-4) 
4. The handler receives `WebhookMetadata.new(topic:, shop: "victim-shop.myshopify.com", body: ..., ...)` and the host application processes/stores the attacker's payload as if it originated from `victim-shop.myshopify.com`.

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
