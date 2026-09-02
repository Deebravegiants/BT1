### Title
Webhook HMAC signature covers only the request body, not the `shop-domain`/`topic`/`webhook-id` headers, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body, so `Utils::HmacValidator.validate` only proves that the *body bytes* were signed by Shopify with the app's `client_secret` — it proves nothing about the `shop-domain`, `topic`, or `webhook-id` headers that `Webhooks::Registry.process` subsequently trusts and hands to the app's webhook handler.

### Finding Description
`Registry.process` authenticates an inbound webhook solely via: [1](#0-0) 

```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
```

`Utils::HmacValidator.validate` computes/compares the signature using `verifiable_query.to_signable_string`: [2](#0-1) 

For `Webhooks::Request`, `to_signable_string` is defined as: [3](#0-2) 

```ruby
def to_signable_string
  @raw_body
end
```

Meanwhile `shop`, `topic`, `api_version`, and `webhook_id` are all pulled straight from unauthenticated HTTP headers, with no cryptographic binding to the HMAC: [4](#0-3) 

The equality the gem actually enforces is:
`hmac_signature == HMAC(client_secret, raw_body)`

but the equality the handler implicitly relies on (via `WebhookMetadata.shop`) is:
`hmac_signature == HMAC(client_secret, raw_body, shop, topic, webhook_id)`

Because `shop` (and `topic`/`webhook_id`) are not part of the signed bytes, any request whose body+HMAC pair is valid for *some* shop will also pass validation with an arbitrary attacker-chosen `shop-domain` header, `topic` header, and `webhook-id` header substituted in.

### Impact Explanation
An unprivileged internet user can install the target public app on their own (free/dev) Shopify store, which causes Shopify to deliver at least one genuine webhook to the app's endpoint — a `(raw_body, hmac-sha256)` pair validly signed with the app's real `client_secret`. The attacker captures this pair, then replays it directly to the app's webhook endpoint while swapping the `X-Shopify-Shop-Domain` header to a victim shop's domain (and optionally the topic/webhook-id headers to a mandatory topic such as `customers/redact` or `shop/redact`, or any topic the host app treats specially). `HmacValidator.validate` still succeeds because it only checks the untouched body bytes, and `Registry.process` forwards `WebhookMetadata` attributing the payload to the victim shop to the host application's handler. This is a cross-tenant identity-binding break: the gem hands the host app data claiming to originate from a shop the request never actually came from, which can lead to spoofed compliance/redaction events, forged order/customer data being processed under the wrong tenant, or other tenant-confusion in the host app — matching the "cross-tenant access" Critical impact category.

### Likelihood Explanation
Requires only: (1) trivial access to a Shopify dev/free store to obtain one legitimately signed webhook body+HMAC pair, and (2) the ability to send an arbitrary HTTP request with custom headers to the target app's public webhook endpoint. No secrets, tokens, or privileged access are needed, making this reachable by any unprivileged internet user.

### Recommendation
Include the security-relevant headers (`shop-domain`, `topic`, `webhook-id`/`api-version`) in the signable string used for HMAC verification, or otherwise cryptographically bind them to the signed payload (e.g., verify shop against a signed field, or require the shop domain to be present in the JSON body and cross-checked). At minimum, document clearly that headers are unauthenticated and host apps must independently verify `shop` against their own webhook-registration records before trusting it, since the gem's `HmacValidator` does not cover them.

### Proof of Concept
1. Attacker installs the target public app on `attacker-shop.myshopify.com`, triggering Shopify to send a real webhook, e.g. for `orders/create`, to the app's registered endpoint, with headers:
   - `X-Shopify-Shop-Domain: attacker-shop.myshopify.com`
   - `X-Shopify-Hmac-Sha256: <valid HMAC of raw_body with app's client_secret>`
   - raw body `B`
2. Attacker captures `B` and the valid `X-Shopify-Hmac-Sha256` value.
3. Attacker sends a new POST to the same endpoint with the same body `B` and the same `X-Shopify-Hmac-Sha256`, but sets `X-Shopify-Shop-Domain: victim-shop.myshopify.com`.
4. `Webhooks::Request#hmac` decodes the same valid signature; `Utils::HmacValidator.validate` recomputes `HMAC(client_secret, B)` and it matches, since `to_signable_string` never included the shop header.
5. `Registry.process` builds `WebhookMetadata` with `shop: "victim-shop.myshopify.com"` and invokes the host app's handler, which now believes the (attacker-controlled) payload legitimately originated from the victim shop.

### Citations

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
