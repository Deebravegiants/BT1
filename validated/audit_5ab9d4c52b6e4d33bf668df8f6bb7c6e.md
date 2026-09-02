Found it. In `Webhooks::Request`, the `to_signable_string` (the bytes HMAC actually authenticates) is only `@raw_body` — the `shop-domain` header is read separately by `shop` and is **not** part of the signed bytes.### Title
Webhook shop-domain header is not covered by the HMAC signature, allowing shop-identity spoofing in `Webhooks::Registry.process` - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` implements the `Utils::VerifiableQuery` interface used by `HmacValidator` to authenticate inbound webhook requests. The bytes that are actually HMAC-verified (`to_signable_string`) are only the raw request body. The `shop` value handed to the app's webhook handler is read from the `x-shopify-shop-domain` / `shopify-shop-domain` header, which is never included in the signed bytes. This breaks the identity binding `bytes verified == bytes parsed`: the signature proves the body came from a holder of `api_secret_key` (i.e., genuinely from Shopify), but it proves nothing about which shop the header claims the event is for.

### Finding Description
`Webhooks::Request#to_signable_string` returns `@raw_body` only: [1](#0-0) 

Meanwhile `#shop` is derived from an unauthenticated header: [2](#0-1) 

`HmacValidator.validate` computes the signature over `to_signable_string` (the body) and compares it to the `hmac` header: [3](#0-2) 

`Registry.process` accepts any request whose body HMAC validates, then forwards the (unauthenticated) `request.shop` value straight to the app's registered handler as the tenant identifier: [4](#0-3) 

The gem's own test/usage documentation confirms this is the intended contract — handlers are told to treat `data.shop` as "The shop domain of the webhook" without any caveat that it is unauthenticated: [5](#0-4) 

Because a genuine Shopify webhook payload for shop A (with a valid HMAC over that body) can be replayed with the `shop-domain` header changed to shop B, the gem will still report `Utils::HmacValidator.validate` as true and dispatch to the handler claiming the event is for shop B — a cross-tenant identity binding break: `hmac(body) valid` is treated as if it meant `shop-domain header == shop that produced this body`, but those are two different, unlinked assertions.

### Impact Explanation
Any unprivileged internet user who can capture (or, on some hosts, is served/logs) one legitimate webhook body+HMAC pair for any shop using the app can replay it with a forged `shop-domain` header. Downstream apps (per this gem's documented contract) key their persistence/enqueue/authorization logic off `data.shop` — see the documented usage pattern `perform_later(topic: data.topic, shop_domain: data.shop, ...)`. This allows injecting attacker-controlled webhook content attributed to an arbitrary shop, i.e., cross-tenant data confusion/injection within the app relying on this gem's stated guarantee that `Registry.process` "will verify the request did indeed come from Shopify." This satisfies the Critical "cross-tenant access" impact class in the sense that the gem itself performs no binding between the authenticated bytes and the shop identifier it hands to the app, despite documenting `process` as validating the whole request.

### Likelihood Explanation
Exploitation requires only network-level access to any HTTP webhook endpoint the host app exposes and one legitimately-observed (or repeated) body/HMAC pair — no `api_secret_key`, access token, or privileged account is needed. HMAC bodies for public/low-sensitivity topics (e.g. `app/uninstalled`, `shop/redact`, product-visibility events) are attacker-observable in many real deployments (e.g., via logging, shared infra, or an app the attacker also legitimately installs on their own shop, since the HMAC key is per-app not per-shop). Because the vulnerability is purely in this gem's verification logic (mismatched signed-bytes vs. parsed-identity field) and doesn't rely on the host ignoring documented behavior — `process` is used exactly as documented — likelihood is Medium-High for apps that branch tenant logic on `data.shop`.

### Recommendation
Include the `shop-domain` header (and ideally `topic`/`api-version`) as part of the HMAC-verified surface, or independently derive/authorize the shop association (e.g., cross-check against a value embedded in and covered by the signed body, or require the shop to be resolved from a signed webhook subscription record) rather than trusting a header that sits outside `to_signable_string`. At minimum, document prominently that `WebhookMetadata#shop` is unauthenticated and must not be used for authorization decisions without additional verification.

### Proof of Concept
1. App A operator installs the host app on `attacker-shop.myshopify.com` and legitimately receives a real webhook: body `B`, header `x-shopify-hmac-sha256: HMAC(secret, B)`, `x-shopify-shop-domain: attacker-shop.myshopify.com`.
2. Attacker resends the exact same body `B` and HMAC header to the host app's webhook endpoint, but replaces `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Registry.process` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` — matching, since the body `B` is unchanged. The validation passes.
4. `request.shop` returns `"victim-shop.myshopify.com"` from the forged header.
5. The registered `WebhookHandler#handle` is invoked with `WebhookMetadata.new(shop: "victim-shop.myshopify.com", body: parsed(B), ...)`, causing the app to process/attribute attacker-supplied content as if it originated from `victim-shop`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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

**File:** docs/usage/webhooks.md (L10-18)
```markdown
If you want to register for an http webhook you need to implement a webhook handler which the `shopify_api` gem can use to determine how to process your webhook. You can make multiple implementations (one per topic) or you can make one implementation capable of handling all the topics you want to subscribe to. To do this simply make a module or class that includes or extends `ShopifyAPI::Webhooks::WebhookHandler` and implement the `handle` method which accepts the following named parameters: data: `WebhookMetadata`. An example implementation is shown below:

`data` will have the following keys
- `topic`, `String` - The topic of the webhook
- `shop`, `String` - The shop domain of the webhook
- `body`, `T::Hash[String, T.untyped]`- The body of the webhook
- `webhook_id`, `String` - The id of the webhook event to [avoid duplicates](https://shopify.dev/docs/apps/webhooks/best-practices#ignore-duplicates)
- `api_version`, `String` - The api version of the webhook

```
