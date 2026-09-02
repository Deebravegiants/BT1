## Title
Webhook shop identity spoofing due to HMAC signature not covering the `shop`/`topic` headers - (`lib/shopify_api/webhooks/request.rb`)

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw HTTP body, so the HMAC that `ShopifyAPI::Webhooks::Registry.process` verifies never binds the `X-Shopify-Shop-Domain` or `X-Shopify-Topic` headers. Any unprivileged merchant who can get Shopify to deliver one legitimately-signed webhook to the app (e.g. by installing the app on a store they control) obtains a signature that stays valid for that exact body forever, and can then be replayed with an arbitrary shop domain and topic to impersonate a different, victim shop.

### Finding Description
The webhook HMAC binding in this gem is: [1](#0-0) 

```ruby
sig { override.returns(String) }
def to_signable_string
  @raw_body
end
```

`shop`, `topic`, `webhook_id`, and `api_version` are all read straight from request headers and are **not** part of the signed string: [2](#0-1) 

The verification path only checks the HMAC over the body, then hands the caller-supplied `shop` and `topic` straight to the handler: [3](#0-2) 

```ruby
def process(request)
  raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)
  handler = @registry[request.topic]&.handler
  ...
  handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
    body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
end
```

`Utils::HmacValidator.validate` computes and compares the signature purely against `verifiable_query.to_signable_string` (the body): [4](#0-3) 

The identity binding that should hold is: **shop-domain-header == shop the HMAC attests to**. Instead, the HMAC only attests to the body; the shop and topic are unauthenticated metadata trusted by the handler. Because Shopify computes webhook HMACs from `api_secret_key` + body only (not headers), a signature obtained for a webhook delivered to shop A's own installation is byte-for-byte reusable for the same body delivered "from" shop B.

### Impact Explanation
Many webhook payloads are shop-independent or trivially predictable (e.g. `app/uninstalled` bodies are typically `{}`, or many topics have static/near-static bodies for a merchant's own actions). An attacker who legitimately installs the target app on their own store (an unprivileged action available to any internet user) will receive a webhook POST with a valid HMAC for that body. Because the gem's verification ignores the `shop`/`topic` headers, the attacker can replay that exact request to the app's webhook endpoint with the `X-Shopify-Shop-Domain` header changed to any victim shop and/or `X-Shopify-Topic` changed to any registered topic. `Utils::HmacValidator.validate` still passes (body unchanged), and the app-side handler receives `WebhookMetadata` claiming to be from the victim shop, e.g. triggering uninstall/deauthorization logic, deleting the victim's stored session, or otherwise mutating state keyed by `shop` — this is a cross-tenant access/integrity break using only the attacker's own valid credentials on their own store.

### Likelihood Explanation
Requires only that the attacker (1) installs/uses the target public app on a store they control to obtain one genuinely-signed webhook, and (2) knows or can guess a topic whose body is shop-independent or attacker-fully-controlled (a large, realistic class of topics, especially shop-level lifecycle topics like `app/uninstalled`, or any topic when the attacker controls the store data entirely). No knowledge of `api_secret_key` or any Shopify-side secret is needed.

### Recommendation
Include `shop`, `topic`, and ideally `webhook_id`/`api_version` in the signed material verified for webhooks, or otherwise cryptographically bind these identity fields to the signature (Shopify's HMAC itself only covers the body, so the fix must happen at the app-consumption layer in this gem, e.g. by requiring/encouraging correlation of `shop` against the caller's known/registered shop list before trusting `WebhookMetadata#shop`, and documenting that `shop`/`topic` headers are unauthenticated and must not be used as the sole tenant-routing key without additional verification).

### Proof of Concept
1. Attacker registers/installs the target Shopify app on their own dev store `attacker-shop.myshopify.com`.
2. Attacker triggers an event whose webhook body is static/predictable, e.g. uninstalls the app to receive an `app/uninstalled` webhook with body `"{}"`, headers:
   ```
   X-Shopify-Topic: app/uninstalled
   X-Shopify-Hmac-Sha256: <valid HMAC of "{}">
   X-Shopify-Shop-Domain: attacker-shop.myshopify.com
   ```
3. Attacker captures this request and re-sends it to the app's webhook endpoint, replacing only the header:
   ```
   X-Shopify-Shop-Domain: victim-shop.myshopify.com
   ```
4. `Utils::HmacValidator.validate` in `lib/shopify_api/utils/hmac_validator.rb` recomputes the HMAC over `"{}"`, which still matches, so `Registry.process` (in `lib/shopify_api/webhooks/registry.rb`) invokes the registered `app/uninstalled` handler with `WebhookMetadata(shop: "victim-shop.myshopify.com", ...)`, causing the app to treat victim-shop as uninstalled/deauthorized even though no such event occurred on that shop.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
