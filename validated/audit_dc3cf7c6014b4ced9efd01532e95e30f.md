### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing shop-identity spoofing in delivered webhook data - (File: `lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC over the raw request body only, while `shop`, `topic`, `api_version`, and `webhook_id` are read directly from unauthenticated HTTP headers. `Registry.process` validates the HMAC and then passes `request.shop` straight into `WebhookMetadata`, which the host application's handler trusts as the authenticated shop identity, even though the shop value itself is never part of what was signed.

### Finding Description
`Utils::HmacValidator.validate` verifies a `VerifiableQuery` by hashing `verifiable_query.to_signable_string` with `Context.api_secret_key` and comparing it against the caller-supplied `hmac`: [1](#0-0) 

For `ShopifyAPI::Webhooks::Request`, `to_signable_string` returns only the raw HTTP body (`@raw_body`) — it does not include the `shop`, `topic`, `api_version`, or `webhook_id` header values in the signed content: [2](#0-1) 

`shop` is read verbatim from the `x-shopify-shop-domain`/`shopify-shop-domain` header with no cryptographic binding to the HMAC: [3](#0-2) [4](#0-3) 

`Registry.process` only checks `Utils::HmacValidator.validate(request)` — i.e., that the body's HMAC is valid for *some* payload signed with the app's secret — and then immediately forwards the unauthenticated `request.shop` (along with `topic`, `webhook_id`, `api_version`) to the handler as though it were a verified field: [5](#0-4) 

The equality the code implicitly assumes is: `shop delivered to handler == shop that produced/authorized this HMAC-signed body`. Because `shop` is excluded from `to_signable_string`, this equality does not hold — any request bearing a body+HMAC pair that is valid for the app's shared `api_secret_key` (e.g., a genuine webhook captured for Shop A, or any body an attacker can get Shopify to sign, since the app secret is shared across all shops installing the app) can be replayed with an arbitrary `x-shopify-shop-domain` header value, and it will pass `HmacValidator.validate` unchanged. The gem then hands the forged `shop` value to the handler as `WebhookMetadata#shop`, which downstream host applications commonly use as the tenant key to look up sessions, write data, or dispatch tenant-scoped side effects, since the gem's own webhook documentation/API implies the `shop` field is authenticated once HMAC validation succeeds.

### Impact Explanation
This breaks the binding between "message authenticated by HMAC" and "shop that is credited with sending it," enabling cross-tenant impersonation at the webhook-consumption layer: an attacker who can trigger or capture one legitimately HMAC-signed webhook body for their own shop (which is under their control, since they own that shop) can relay/replay it against the app's webhook endpoint while substituting the `shop-domain` header for a victim shop. Because the gem still reports the check as valid and exposes the attacker-controlled `shop` value to the handler, applications relying on `HmacValidator`/`Registry.process` for tenant isolation are misled into attributing attacker-supplied webhook content to a shop the attacker does not control — a cross-tenant identity confusion originating entirely within this gem's trust boundary (the app never needed the victim's credentials).

### Likelihood Explanation
Medium: any developer using an app's own shop to legitimately trigger a webhook topic under their control (e.g., `orders/create` in their own store) obtains a validly signed body+HMAC pair, since `api_secret_key` is shared by the app across all installed shops rather than being shop-specific. Swapping only the `shop-domain` header before replaying to the app's webhook endpoint requires no secret material and no privileged access — it is exploitable by any unprivileged actor who can install/operate a shop under the app and control an HTTP client, matching the "unprivileged internet user" threat model.

### Recommendation
Include `shop` (and ideally `topic`, `webhook_id`, `api_version`) in the HMAC-signed content, or otherwise cryptographically bind the shop identity to the payload before exposing it to handlers. At minimum, `Webhooks::Request#to_signable_string` should incorporate the `shop-domain` header value (e.g., signing `"#{shop}\n#{@raw_body}"` consistent with how Shopify signs the header) so that `HmacValidator.validate` fails if the shop header is altered independently of the signed body.

### Proof of Concept
1. App has `api_secret_key` shared across all shops that install it.
2. Attacker installs/owns "attacker-shop.myshopify.com" and triggers a webhook event (e.g. creates an order) so Shopify sends a legitimately signed webhook: body `B`, header `x-shopify-hmac-sha256: HMAC(secret, B)`, `x-shopify-shop-domain: attacker-shop.myshopify.com`.
3. Attacker intercepts this request (their own webhook, so they can simply capture it via a proxy) and replays it to the app's webhook endpoint, changing only `x-shopify-shop-domain` to `victim-shop.myshopify.com`, keeping `B` and the HMAC header identical.
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes the HMAC over `to_signable_string` (== `B`) only — passes, because `B` and its HMAC are unchanged: [6](#0-5) .
5. The handler receives `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and attacker-controlled body content, believing it originated from the victim shop: [7](#0-6) .

### Citations

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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

**File:** lib/shopify_api/webhooks/request.rb (L67-70)
```ruby
      sig { params(name: String).returns(T.untyped) }
      def shopify_header(name)
        @headers["shopify-#{name}"] || @headers["x-shopify-#{name}"]
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
